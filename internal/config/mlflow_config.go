package config

import (
	"crypto/tls"
	"time"
)

type MLFlowConfig struct {
	TrackingURI string        `mapstructure:"tracking_uri"`
	HTTPTimeout time.Duration `mapstructure:"http_timeout"`
	Secure      bool          `mapstructure:"secure"`
	TLSConfig   *tls.Config   // not serialized
}
