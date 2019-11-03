package main

import (
	"github.com/gin-gonic/gin"
)


func main() {
	// Disable Console Color, you don't need console color when writing the logs to file.
	// gin.DisableConsoleColor()

	// Logging to a file.
	// f, _ := os.Create("server_sre_sms.log")
	// gin.DefaultWriter = io.MultiWriter(f)

	app := gin.Default()

	app.GET("/status", func(c *gin.Context) {c.JSON(200, gin.H{"message": "pong",})})

	// run
	err := app.Run(":4000" )
	if err != nil {
		panic(err)
	}
}
