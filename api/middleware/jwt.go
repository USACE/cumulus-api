package middleware

import (
	"github.com/golang-jwt/jwt"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

const (
	developPublicKey = `-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAnPq4vHhlaGYzGtEnEXe1
vQoFBCBeCmOoIXUya1TpVbrscLRrBXLzDdqBnOyNZfAFvzEj1ghZTlpecATiL6C6
O8PAVdFF82Jf+8NmbMzw2a1AUjhtxLrvxOmqwg/yn7e2wLol9xnml4bbGr0iIszK
wNEPHUlDvBR4APYjH9DkPDpG+wYRUKuoIKNEEQf/uhUEyJdn1Bx+1ge5m1n91Ibo
K0Y2wn6mR85RHc5t+50iGQTXz7xJwPjSZQcoZjSB4T0WL2CjdsHqyVxjX0L3TuF8
6VnohzkSLDuEMfciuRi+VTDKawcMvDUoijtbJHPe9iZqpa7LeLFk2cxfBei8waOI
FCC1Sh4YZWpnXpgcnQ5KIT0yKq2WVIBSsCUBfUCwM0QaiaPjyIkYlBKIvPKjfHj5
s7hWTDC2yBU4npTWhi/y57kCgYbOJjj3SEy8Kb23VYF85TvVEnDSahmooMi6642n
c+CCk5UUv0bASlkMRAH8UupA7ZDSUbwz7ZfAOWvz/qGZRcuuPWa6c/doxaK5hgff
hjy0qHQj/rbT08qC6OF3vop9z25aljgMsszamwQJKM4hCLTdfwJeFJ8MK/5BwzB9
3jnqcRyu7toZPQxOuJp1Ckd2xqMB1DsmzNFiWDvH59FoK3UboxdF4zzZGbgqDXBv
tLLHT5MavkIhYxaAh33D8s8CAwEAAQ==
-----END PUBLIC KEY-----`

	stablePublicKey = `-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAk2rbR10Rh5okYkWTaKaD
0wg3e/TxK0+SxsoZJ1ECLaeQDaRNuZb7WlJjAm2k0E//6v5ypohKljsCEmQemlcf
hgAg7as42Mky3ikTvCsLE4YKm85kqsfKz4UJHYijVqJYpfmuFFl07LZIXAIHneeW
Rdz3q3ALtyTQQ3aa8f00usJOE2QAM7dOHQXQls7E2k2Obyb1msWYYdb6cx+rxJrS
nwEHcrLvecVjYh4yIpSa6E8FwG0Z5/ewog+iwXRejGS5KwIBnRPtVcndSOIepJ/O
5yyeFwNs9fc1TzMedsD2BOjghYDoqE/+ELRt5RlFurKTA7U2eZ2wiqAcwH+Dv80j
rI10jMgqxBBlyq33jOm+GTSotUJTr+dNUnS1SZWExw+xdAcj7PzRMwh9tmIfEnMW
H2vt+4YZxuGNqXYsEYp3E4BYQaLqS9qypldxRW9JZ2by7n2Ar1UYPJO/KImSr0xv
oUNi8GabG71lhe0W9oMDTii7V2sotmJd1kP8E815U8pABDy2q/elqWmIYSJTIhdr
Jng+cOOaf/ZGA0qe8AHhMNZHvRVopOGSsVNtIOhDFqVJN9NKuJZ+sjihiwPymcam
8oCYMHjKRSXUSGmoYLbIFwznpBF5Tu78X6eZBBOr06uoMW7Noy4+I8btrgGNmwXf
a98Xst+8TrgTq3+jKBvAVEMCAwEAAQ==
-----END PUBLIC KEY-----`
)

var skipper = func(c echo.Context) bool {
	if c.QueryParam("key") != "" {
		return true
	}
	return false
}

var JWTDevelop = middleware.JWTWithConfig(middleware.JWTConfig{
	SigningMethod: "RS512",
	KeyFunc: func(t *jwt.Token) (interface{}, error) {
		return jwt.ParseRSAPublicKeyFromPEM([]byte(developPublicKey))
	},
	Skipper: skipper,
})

var JWTStable = middleware.JWTWithConfig(middleware.JWTConfig{
	SigningMethod: "RS512",
	KeyFunc: func(t *jwt.Token) (interface{}, error) {
		return jwt.ParseRSAPublicKeyFromPEM([]byte(stablePublicKey))
	},
	Skipper: skipper,
})

var JWTMock = middleware.JWTWithConfig(middleware.JWTConfig{
	SigningKey: []byte("mock"),
	Skipper:    skipper,
})
