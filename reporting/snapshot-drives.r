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
df = read.csv(paste(path_to_snapshot, "/", "drives.csv", sep=""), sep=",", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%Y-%m-%d %H:%M:%S"))


# Convert to long format
mdf <- melt(df, id.vars = "datetime")



# Prepare plot.
p = ggplot(mdf, aes(x=datetime, value))
p = p + geom_line(aes(color=variable, alpha = 0.25,))
p = p + stat_smooth(aes(colour=variable))
p = p + scale_alpha(guide = 'none')
p = p + ylab("drives")
ggsave(p, file=paste(path_to_output, "/", "drives-timeseries.pdf", sep=""), width=10, height=3, scale=1)

