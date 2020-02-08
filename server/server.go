package server

import (
	"sre-sms/server/middleware/auth"

	"github.com/gin-gonic/gin"
	"github.com/robfig/cron/v3"
)

// Run start a http server use gin
func Run() {
	auth.LoadAuthData()
	c := cron.New()
	c.AddFunc("@every 10s", auth.LoadAuthData)
	c.Start()
	app := gin.Default()
	app.GET("/status", func(c *gin.Context) { c.JSON(200, gin.H{"message": "pong"}) })

	authorized := app.Group("/sms", auth.BasicAuth())
	authorized.GET("/send", func(c *gin.Context) { c.JSON(200, gin.H{"message": "pong"}) })

	err := app.Run(":4000")
	if err != nil {
		panic(err)
	}
}
