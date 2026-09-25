package costs

import (
	"context"
	"fmt"
	"log"
	"math"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatch"
	"github.com/aws/aws-sdk-go-v2/service/cloudwatch/types"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/USACE/cumulus-api/api/models"
)

const (
	// AWS bills monthly quantities (GB-month, per-month fees) against a
	// 730-hour month.
	hoursPerMonth = 730.0
	bytesPerGB    = 1 << 30
	day           = 24 * time.Hour
)

// Line is one cost category across the three reporting periods.
type Line struct {
	Category   string  `json:"category"`
	Detail     string  `json:"detail"`
	Source     string  `json:"source"` // cloudwatch, database, or config
	Monthly    float64 `json:"monthly"`
	YearToDate float64 `json:"year_to_date"`
	SinceStart float64 `json:"since_start"`
}

type Period struct {
	Start time.Time `json:"start"`
	End   time.Time `json:"end"`
	Total float64   `json:"total"`
}

// Estimate is the admin cost estimate. Monthly is a run rate: the last 30
// days' usage scaled to a 730-hour month.
type Estimate struct {
	GeneratedAt time.Time `json:"generated_at"`
	Currency    string    `json:"currency"`
	Monthly     Period    `json:"monthly"`
	YearToDate  Period    `json:"year_to_date"`
	SinceStart  Period    `json:"since_start"`
	Lines       []Line    `json:"lines"`
	Omitted     []Line    `json:"omitted"`
	Notes       []string  `json:"notes"`
}

// Estimator computes the estimate and caches it for Config.CacheTTL, so page
// loads don't each hit CloudWatch and the download table.
type Estimator struct {
	cfg Config
	cw  *cloudwatch.Client
	db  *pgxpool.Pool

	mu     sync.Mutex
	cached *Estimate
}

func NewEstimator(cfg Config, cw *cloudwatch.Client, db *pgxpool.Pool) *Estimator {
	return &Estimator{cfg: cfg, cw: cw, db: db}
}

// Get returns the cached estimate, recomputing it once it is older than the
// TTL. Holding the lock while computing means concurrent callers wait for one
// computation instead of each starting their own.
func (e *Estimator) Get(ctx context.Context) (*Estimate, error) {
	e.mu.Lock()
	defer e.mu.Unlock()
	if e.cached != nil && time.Since(e.cached.GeneratedAt) < e.cfg.CacheTTL {
		return e.cached, nil
	}
	est, err := e.compute(ctx)
	if err != nil {
		return nil, err
	}
	e.cached = est
	return est, nil
}

// window is a reporting period. hours is the length costs are scaled to,
// which differs from to-from only for the monthly run rate.
type window struct {
	from, to time.Time
	hours    float64
}

// scale converts usage measured over the window into its billed length.
func (w window) scale() float64 {
	actual := w.to.Sub(w.from).Hours()
	if actual <= 0 {
		return 0
	}
	return w.hours / actual
}

// series is a daily metric, keyed by the Unix time of the UTC midnight
// starting each day. (Unix seconds rather than time.Time, whose map equality
// also compares Location.)
type series map[int64]float64

// valueHours integrates a daily series over [from, to): each day's value
// times the hours of that day inside the window. Days after the newest
// datapoint carry it forward (S3 storage metrics lag a day or two); any other
// day with no datapoint uses fallback.
func (s series) valueHours(from, to time.Time, fallback float64) float64 {
	last, haveLast := s.lastDay()
	var sum float64
	for d := from.Truncate(day); d.Before(to); d = d.Add(day) {
		start, end := d, d.Add(day)
		if start.Before(from) {
			start = from
		}
		if end.After(to) {
			end = to
		}
		v, ok := s[d.Unix()]
		switch {
		case ok:
		case haveLast && d.Unix() > last:
			v = s[last]
		default:
			v = fallback
		}
		sum += v * end.Sub(start).Hours()
	}
	return sum
}

func (s series) lastDay() (int64, bool) {
	var last int64
	for t := range s {
		if t > last {
			last = t
		}
	}
	return last, len(s) > 0
}

func (s series) latest() (float64, bool) {
	last, ok := s.lastDay()
	return s[last], ok
}

func (e *Estimator) compute(ctx context.Context) (*Estimate, error) {
	cfg := e.cfg
	now := time.Now().UTC()
	ytdStart := time.Date(now.Year(), 1, 1, 0, 0, 0, 0, time.UTC)
	start := cfg.start
	if start.IsZero() {
		start = ytdStart
	}
	if start.After(now) {
		start = now
	}
	windows := [3]window{
		{from: now.Add(-30 * day), to: now, hours: hoursPerMonth},
		{from: ytdStart, to: now, hours: now.Sub(ytdStart).Hours()},
		{from: start, to: now, hours: now.Sub(start).Hours()},
	}

	notes := []string{
		"Estimate only, from public AWS GovCloud (us-gov-west-1) on-demand prices. Excludes taxes, credits, support, and shared CWBI infrastructure.",
		"Egress counts only download packages (size x retrieval count, dated by last retrieval). COG streaming and API responses are not included.",
		"Volume tiers (S3 over 50 TB, egress over 10 TB) are not applied.",
		fmt.Sprintf("Lines under $%.2f/month are listed under omitted and excluded from totals.", cfg.MinMonthly),
	}
	if cfg.NATCount == 0 {
		notes = append(notes, "NAT gateways are excluded (COST_NAT_COUNT=0).")
	}

	metricFrom := start
	for _, w := range windows {
		if w.from.Before(metricFrom) {
			metricFrom = w.from
		}
	}
	metrics, err := e.fetchMetrics(ctx, metricFrom.Truncate(day), now)
	if err != nil {
		log.Printf("cost estimate: CloudWatch GetMetricData failed: %v", err)
		notes = append(notes, "CloudWatch metrics were unavailable; Fargate task counts and S3 storage use configured values.")
		metrics = map[string]series{}
	}

	var lines []Line
	add := func(category, detail, source string, cost func(w window) float64) {
		l := Line{Category: category, Detail: detail, Source: source}
		l.Monthly = cost(windows[0])
		l.YearToDate = cost(windows[1])
		l.SinceStart = cost(windows[2])
		lines = append(lines, l)
	}

	// Fargate, one line per service.
	for _, svc := range cfg.services {
		svc := svc
		tasks := metrics["task:"+svc.Name]
		perTaskHour := svc.VCPU*cfg.FargateVCPUHour + svc.MemGB*cfg.FargateGBHour
		source, taskDetail := "config", fmt.Sprintf("%g task(s)", svc.Tasks)
		if len(tasks) > 0 {
			source, taskDetail = "cloudwatch", "task count from LiveTaskCount"
		}
		add("Fargate: "+svc.Name,
			fmt.Sprintf("%g vCPU / %g GB per task, %s", svc.VCPU, svc.MemGB, taskDetail),
			source,
			func(w window) float64 {
				return tasks.valueHours(w.from, w.to, svc.Tasks) * perTaskHour * w.scale()
			})
	}

	// RDS.
	add("RDS instance", cfg.RDSInstanceClass+" Single-AZ PostgreSQL", "config",
		func(w window) float64 { return cfg.RDSInstanceHour * w.hours })
	rdsDetail := fmt.Sprintf("%g GB gp3 allocated", cfg.RDSStorageGB)
	if free, ok := metrics["rdsfree"].latest(); ok {
		rdsDetail += fmt.Sprintf(", %.0f GB used", cfg.RDSStorageGB-free/bytesPerGB)
	}
	add("RDS storage", rdsDetail, "config",
		func(w window) float64 { return cfg.RDSStorageGB * cfg.RDSStorageGBMonth * w.hours / hoursPerMonth })

	// S3 storage, priced per storage class.
	storageTypes := make([]string, 0, len(cfg.S3StorageRates))
	for st := range cfg.S3StorageRates {
		storageTypes = append(storageTypes, st)
	}
	sort.Strings(storageTypes)
	var haveS3 bool
	var s3Detail []string
	for _, st := range storageTypes {
		if b, ok := metrics["s3:"+st].latest(); ok {
			haveS3 = true
			s3Detail = append(s3Detail, fmt.Sprintf("%s %.1f GB", st, b/bytesPerGB))
		}
	}
	if haveS3 {
		add("S3 storage", cfg.S3Bucket+": "+strings.Join(s3Detail, ", "), "cloudwatch",
			func(w window) float64 {
				var cost float64
				for _, st := range storageTypes {
					gbHours := metrics["s3:"+st].valueHours(w.from, w.to, 0) / bytesPerGB
					cost += gbHours * cfg.S3StorageRates[st] / hoursPerMonth
				}
				return cost * w.scale()
			})
	} else {
		add("S3 storage", fmt.Sprintf("%s: %g GB assumed at StandardStorage rate", cfg.S3Bucket, cfg.S3FallbackGB), "config",
			func(w window) float64 {
				return cfg.S3FallbackGB * cfg.S3StorageRates["StandardStorage"] * w.hours / hoursPerMonth
			})
	}
	if objects := metrics["s3objects"]; len(objects) > 0 {
		// NumberOfObjects counts every object, not just Intelligent-Tiering
		// ones over the 128 KB monitoring minimum, so this overstates the fee.
		add("S3 Intelligent-Tiering monitoring", "total object count (upper bound)", "cloudwatch",
			func(w window) float64 {
				return objects.valueHours(w.from, w.to, 0) * cfg.S3MonitoringPerObject / hoursPerMonth * w.scale()
			})
	}
	add("S3 requests", fmt.Sprintf("%g PUT + %g GET per month", cfg.S3PutsPerMonth, cfg.S3GetsPerMonth), "config",
		func(w window) float64 {
			return (cfg.S3PutsPerMonth*cfg.S3PutRate + cfg.S3GetsPerMonth*cfg.S3GetRate) * w.hours / hoursPerMonth
		})

	// Egress from the download usage tracking.
	var egress [3]float64
	for i, w := range windows {
		b, err := models.DownloadEgressBytes(ctx, e.db, w.from, w.to)
		if err != nil {
			return nil, fmt.Errorf("download egress: %w", err)
		}
		egress[i] = float64(b) / bytesPerGB * cfg.EgressGBRate * w.scale()
	}
	lines = append(lines, Line{
		Category: "Internet egress (downloads)", Detail: fmt.Sprintf("download packages at $%g/GB", cfg.EgressGBRate), Source: "database",
		Monthly: egress[0], YearToDate: egress[1], SinceStart: egress[2],
	})

	// Fixed-size infrastructure from config.
	add("Application load balancer", fmt.Sprintf("%g ALB, %g LCU average", cfg.ALBCount, cfg.ALBLCUs), "config",
		func(w window) float64 { return cfg.ALBCount * (cfg.ALBHour + cfg.ALBLCUs*cfg.ALBLCUHour) * w.hours })
	add("NAT gateways", fmt.Sprintf("%g gateway(s), %g GB/month", cfg.NATCount, cfg.NATGBMonth), "config",
		func(w window) float64 {
			return cfg.NATCount*cfg.NATHour*w.hours + cfg.NATGBMonth*cfg.NATGBRate*w.hours/hoursPerMonth
		})
	add("CloudWatch Logs ingestion", fmt.Sprintf("%g GB/month", cfg.LogsIngestGBMonth), "config",
		func(w window) float64 { return cfg.LogsIngestGBMonth * cfg.LogsIngestRate * w.hours / hoursPerMonth })
	add("CloudWatch Logs storage", fmt.Sprintf("%g GB retained", cfg.LogsStoredGB), "config",
		func(w window) float64 { return cfg.LogsStoredGB * cfg.LogsStorageRate * w.hours / hoursPerMonth })
	add("CloudWatch metrics and alarms", fmt.Sprintf("%g metrics, %g alarms", cfg.CWMetrics, cfg.CWAlarms), "config",
		func(w window) float64 {
			return (cfg.CWMetrics*cfg.CWMetricRate + cfg.CWAlarms*cfg.CWAlarmRate) * w.hours / hoursPerMonth
		})
	add("ECR", fmt.Sprintf("%g GB of images", cfg.ECRGB), "config",
		func(w window) float64 { return cfg.ECRGB * cfg.ECRGBRate * w.hours / hoursPerMonth })

	est := &Estimate{
		GeneratedAt: now,
		Currency:    "USD",
		Monthly:     Period{Start: windows[0].from, End: now},
		YearToDate:  Period{Start: ytdStart, End: now},
		SinceStart:  Period{Start: start, End: now},
		Lines:       []Line{},
		Omitted:     []Line{},
		Notes:       notes,
	}
	for _, l := range lines {
		l.Monthly, l.YearToDate, l.SinceStart = round2(l.Monthly), round2(l.YearToDate), round2(l.SinceStart)
		if l.Monthly < cfg.MinMonthly {
			est.Omitted = append(est.Omitted, l)
			continue
		}
		est.Lines = append(est.Lines, l)
		est.Monthly.Total += l.Monthly
		est.YearToDate.Total += l.YearToDate
		est.SinceStart.Total += l.SinceStart
	}
	est.Monthly.Total = round2(est.Monthly.Total)
	est.YearToDate.Total = round2(est.YearToDate.Total)
	est.SinceStart.Total = round2(est.SinceStart.Total)
	return est, nil
}

// fetchMetrics reads every daily CloudWatch series the estimate uses in one
// paginated GetMetricData call. Keys: "task:<service>", "s3:<storage type>",
// "s3objects", "rdsfree".
func (e *Estimator) fetchMetrics(ctx context.Context, from, to time.Time) (map[string]series, error) {
	cfg := e.cfg
	type query struct {
		key, namespace, metric string
		dims                   []types.Dimension
	}
	dim := func(name, value string) types.Dimension {
		return types.Dimension{Name: aws.String(name), Value: aws.String(value)}
	}
	var queries []query
	for _, svc := range cfg.services {
		queries = append(queries, query{"task:" + svc.Name, "AWS/ECS", "LiveTaskCount",
			[]types.Dimension{dim("ClusterName", cfg.ECSCluster), dim("ServiceName", svc.Name)}})
	}
	for st := range cfg.S3StorageRates {
		queries = append(queries, query{"s3:" + st, "AWS/S3", "BucketSizeBytes",
			[]types.Dimension{dim("BucketName", cfg.S3Bucket), dim("StorageType", st)}})
	}
	queries = append(queries,
		query{"s3objects", "AWS/S3", "NumberOfObjects",
			[]types.Dimension{dim("BucketName", cfg.S3Bucket), dim("StorageType", "AllStorageTypes")}},
		query{"rdsfree", "AWS/RDS", "FreeStorageSpace",
			[]types.Dimension{dim("DBInstanceIdentifier", cfg.RDSInstanceID)}},
	)

	// GetMetricData ids must start with a lowercase letter, so map q0, q1, ...
	// back to the keys.
	keyByID := make(map[string]string, len(queries))
	mdq := make([]types.MetricDataQuery, 0, len(queries))
	for i, q := range queries {
		id := fmt.Sprintf("q%d", i)
		keyByID[id] = q.key
		mdq = append(mdq, types.MetricDataQuery{
			Id: aws.String(id),
			MetricStat: &types.MetricStat{
				Metric: &types.Metric{Namespace: aws.String(q.namespace), MetricName: aws.String(q.metric), Dimensions: q.dims},
				Period: aws.Int32(int32(day.Seconds())),
				Stat:   aws.String("Average"),
			},
			ReturnData: aws.Bool(true),
		})
	}

	ctx, cancel := context.WithTimeout(ctx, 20*time.Second)
	defer cancel()
	out := make(map[string]series, len(queries))
	p := cloudwatch.NewGetMetricDataPaginator(e.cw, &cloudwatch.GetMetricDataInput{
		StartTime:         aws.Time(from),
		EndTime:           aws.Time(to),
		MetricDataQueries: mdq,
	})
	for p.HasMorePages() {
		page, err := p.NextPage(ctx)
		if err != nil {
			return nil, err
		}
		for _, r := range page.MetricDataResults {
			key := keyByID[aws.ToString(r.Id)]
			if out[key] == nil {
				out[key] = series{}
			}
			for i, t := range r.Timestamps {
				out[key][t.UTC().Truncate(day).Unix()] = r.Values[i]
			}
		}
	}
	return out, nil
}

func round2(v float64) float64 { return math.Round(v*100) / 100 }
