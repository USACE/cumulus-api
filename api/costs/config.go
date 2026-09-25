package costs

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/kelseyhightower/envconfig"
)

// Config holds the rates and resource sizes behind the admin cost estimate.
//
// Default rates are AWS GovCloud (US-West, us-gov-west-1) on-demand prices
// taken from the public AWS Price List API (publication 2026-09-18), except
// the NAT gateway rates, which are unverified estimates. Every value is
// env-overridable (COST_*), so a price or size change is a config change, not
// a code change.
type Config struct {
	// StartDate (YYYY-MM-DD) is where the "since_start" running total begins.
	// Empty means Jan 1 of the current year, i.e. the same as year-to-date.
	StartDate string `envconfig:"COST_START_DATE"`
	// Lines whose estimated monthly cost is below this are reported under
	// "omitted" and left out of the totals.
	MinMonthly float64       `envconfig:"COST_MIN_MONTHLY" default:"5"`
	CacheTTL   time.Duration `envconfig:"COST_CACHE_TTL" default:"1h"`

	// Fargate. Each service is "name:vcpu:memory_gb:tasks". Task counts are
	// replaced by the CloudWatch AWS/ECS LiveTaskCount metric where it has data;
	// the configured count fills any day without a datapoint.
	ECSCluster      string   `envconfig:"COST_ECS_CLUSTER" default:"cumulus-cluster"`
	FargateServices []string `envconfig:"COST_FARGATE_SERVICES" default:"cumulus-api:0.5:1:1,cumulus-geoprocess:1:2:2,cumulus-listener:0.5:1:1,cumulus-packager:2:4:2,cumulus-pg_featureserv:0.5:1:1"`
	FargateVCPUHour float64  `envconfig:"COST_FARGATE_VCPU_HOUR" default:"0.0486"`
	FargateGBHour   float64  `envconfig:"COST_FARGATE_GB_HOUR" default:"0.0053"`

	// RDS (Single-AZ PostgreSQL). Billing is on allocated storage;
	// FreeStorageSpace is only read to report how much of it is used.
	RDSInstanceID     string  `envconfig:"COST_RDS_INSTANCE_ID" default:"cumulus"`
	RDSInstanceClass  string  `envconfig:"COST_RDS_INSTANCE_CLASS" default:"db.t4g.medium"`
	RDSInstanceHour   float64 `envconfig:"COST_RDS_INSTANCE_HOUR" default:"0.07"`
	RDSStorageGB      float64 `envconfig:"COST_RDS_STORAGE_GB" default:"400"`
	RDSStorageGBMonth float64 `envconfig:"COST_RDS_STORAGE_GB_MONTH" default:"0.138"`

	// S3 storage, priced per CloudWatch BucketSizeBytes StorageType. Only the
	// storage types listed here are queried. S3FallbackGB (priced at the
	// StandardStorage rate) is used only when CloudWatch can't be reached.
	S3Bucket       string             `envconfig:"COST_S3_BUCKET" default:"cumulus-prod"`
	S3StorageRates map[string]float64 `envconfig:"COST_S3_STORAGE_RATES" default:"StandardStorage:0.039,IntelligentTieringFAStorage:0.039,IntelligentTieringIAStorage:0.02,IntelligentTieringAIAStorage:0.0064,GlacierInstantRetrievalStorage:0.0064,GlacierIRSizeOverhead:0.0064"`
	S3FallbackGB   float64            `envconfig:"COST_S3_FALLBACK_GB" default:"1024"`
	// Intelligent-Tiering monitoring, per object per month.
	S3MonitoringPerObject float64 `envconfig:"COST_S3_MONITORING_PER_OBJECT" default:"0.0000025"`
	S3PutsPerMonth        float64 `envconfig:"COST_S3_PUTS_PER_MONTH" default:"1000000"`
	S3PutRate             float64 `envconfig:"COST_S3_PUT_RATE" default:"0.000005"`
	S3GetsPerMonth        float64 `envconfig:"COST_S3_GETS_PER_MONTH" default:"10000000"`
	S3GetRate             float64 `envconfig:"COST_S3_GET_RATE" default:"0.0000004"`

	// Internet egress, first-10-TB tier. Volume comes from the download table.
	EgressGBRate float64 `envconfig:"COST_EGRESS_GB_RATE" default:"0.155"`

	ALBCount   float64 `envconfig:"COST_ALB_COUNT" default:"1"`
	ALBHour    float64 `envconfig:"COST_ALB_HOUR" default:"0.032"`
	ALBLCUs    float64 `envconfig:"COST_ALB_LCUS" default:"0"`
	ALBLCUHour float64 `envconfig:"COST_ALB_LCU_HOUR" default:"0.01"`

	// NAT is off by default: the account's NAT gateways are shared and which
	// ones carry Cumulus traffic isn't known yet.
	NATCount   float64 `envconfig:"COST_NAT_COUNT" default:"0"`
	NATHour    float64 `envconfig:"COST_NAT_HOUR" default:"0.054"`
	NATGBMonth float64 `envconfig:"COST_NAT_GB_MONTH" default:"0"`
	NATGBRate  float64 `envconfig:"COST_NAT_GB_RATE" default:"0.054"`

	LogsIngestGBMonth float64 `envconfig:"COST_LOGS_INGEST_GB_MONTH" default:"100"`
	LogsIngestRate    float64 `envconfig:"COST_LOGS_INGEST_RATE" default:"0.675"`
	LogsStoredGB      float64 `envconfig:"COST_LOGS_STORED_GB" default:"100"`
	LogsStorageRate   float64 `envconfig:"COST_LOGS_STORAGE_RATE" default:"0.039"`
	CWMetrics         float64 `envconfig:"COST_CW_METRICS" default:"20"`
	CWMetricRate      float64 `envconfig:"COST_CW_METRIC_RATE" default:"0.30"`
	CWAlarms          float64 `envconfig:"COST_CW_ALARMS" default:"10"`
	CWAlarmRate       float64 `envconfig:"COST_CW_ALARM_RATE" default:"0.13"`

	ECRGB     float64 `envconfig:"COST_ECR_GB" default:"50"`
	ECRGBRate float64 `envconfig:"COST_ECR_GB_RATE" default:"0.10"`

	services []service
	start    time.Time
}

type service struct {
	Name  string
	VCPU  float64
	MemGB float64
	Tasks float64
}

// LoadConfig reads the COST_* environment variables.
func LoadConfig() (Config, error) {
	var c Config
	if err := envconfig.Process("cumulus", &c); err != nil {
		return c, err
	}
	for _, s := range c.FargateServices {
		p := strings.Split(strings.TrimSpace(s), ":")
		if len(p) != 4 {
			return c, fmt.Errorf("COST_FARGATE_SERVICES entry %q: want name:vcpu:memory_gb:tasks", s)
		}
		var nums [3]float64
		for i, raw := range p[1:] {
			v, err := strconv.ParseFloat(raw, 64)
			if err != nil {
				return c, fmt.Errorf("COST_FARGATE_SERVICES entry %q: %w", s, err)
			}
			nums[i] = v
		}
		c.services = append(c.services, service{Name: p[0], VCPU: nums[0], MemGB: nums[1], Tasks: nums[2]})
	}
	if c.StartDate != "" {
		t, err := time.Parse("2006-01-02", c.StartDate)
		if err != nil {
			return c, fmt.Errorf("COST_START_DATE: %w", err)
		}
		c.start = t
	}
	return c, nil
}
