#!/usr/bin/env Rscript
library(ggplot2) 
library(scales)
library(plyr)
library(reshape2)

# accept snapshot path? -> populate, ensure directory structure ($snapshot/plots/..)
source("helper-snapshot-arguments.r")
#path_to_snapshot = "./2017-03-16T17:15:39.685334_43f835ce2f"
#path_to_output   = "."
print(path_to_snapshot)
print(path_to_output)
if ( !exists("path_to_snapshot") && !exists("path_to_output") ) {
	stop("Input and output paths are not defined!", call.=FALSE)
}


# Load data from snapshot
df = read.csv(paste(path_to_snapshot, "/wait-times.csv", sep=""), sep=",", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%Y-%m-%d %H:%M:%S"))

# plot options
num_bins = 50000
freqpoly_factor = 5
limits = c(as.POSIXct("2016-01-17"), as.POSIXct("2016-02-06 01:00:00"))
weeks <- data.frame(Date=seq(as.POSIXct("2015-12-01"), limits[2], by="weeks"))


# alter data
df = df[ , !(names(df) %in% c("count"))]
mdf <- melt(df, id.vars = "datetime")


p = ggplot(mdf, aes(datetime, value, fill = variable, width=15000))
#p = p + geom_bar(stat='identity') #  stacked
p = p + geom_bar(stat='identity', position="dodge") #
p = p + theme(legend.text=element_text(size=8), legend.key.height=unit(0.75, "line")) + ylab("Number of Jobs") + xlab(NULL)
p = p + scale_fill_discrete("wait-times", 
                      breaks=c("X1m","X2m","X3m","X4m","X5m","X8m","X10m","X15m","X20m","X30m","X1h","X2h","X4h","X8h", "more"), 
                      labels=c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more"))


p = p + geom_vline(data=weeks, xintercept=as.numeric(weeks$Date), linetype="longdash", size=0.2, alpha=0.5)
#p = p + theme(legend.position="bottom")
#p = p + theme_bw() 
ggsave(p, file=paste(path_to_output, "/", "waiting-timeseries.pdf", sep=""), width=10, height=3, scale=1)
