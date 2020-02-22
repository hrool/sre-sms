package server

import (
	"github.com/robfig/cron/v3"
	"sre-sms/server/middleware/auth"
)

func init() {
	//tasks.Init()
	auth.LoadAuthData()
	c := cron.New()
	c.AddFunc("@every 10s", auth.LoadAuthData)
	c.Start()
}
