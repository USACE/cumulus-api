package models

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"time"

	"github.com/google/uuid"
)

// SignDownloadLink returns an expiry timestamp and HMAC signature authorizing
// fetches of a single download's completed file until exp.
func SignDownloadLink(secret string, downloadID uuid.UUID, ttl time.Duration) (exp int64, sig string) {
	exp = time.Now().Add(ttl).Unix()
	return exp, downloadLinkSignature(secret, downloadID, exp)
}

// ValidDownloadLink reports whether sig is a valid, unexpired signature for downloadID.
func ValidDownloadLink(secret string, downloadID uuid.UUID, exp int64, sig string) bool {
	if time.Now().Unix() > exp {
		return false
	}
	expected := downloadLinkSignature(secret, downloadID, exp)
	return hmac.Equal([]byte(sig), []byte(expected))
}

func downloadLinkSignature(secret string, downloadID uuid.UUID, exp int64) string {
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte(fmt.Sprintf("%s.%d", downloadID, exp)))
	return hex.EncodeToString(mac.Sum(nil))
}
