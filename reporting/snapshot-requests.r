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
df = read.csv(paste(path_to_snapshot, "/requests.csv", sep=""), sep=",", header=TRUE)
df$occur <- as.POSIXct(strptime(df$occur, "%Y-%m-%d %H:%M:%S"))
df$finish <- as.POSIXct(strptime(df$finish, "%Y-%m-%d %H:%M:%S"))


# Convert to long format
mdf <- melt(df, id.vars = "rid")


# Candidate Plots
# Timeseries:  Start - End;   x=time,   y = request?    comment: maybe not so useful
# Timerseries: read vs. write

# Distribution: Size, Duration  (also by type)

###############################################################################
# SIZE
# hist
p = ggplot(df, aes(x=megabytes))
p = p + geom_histogram() + expand_limits(y = 0)
ggsave(p, file=paste(path_to_output, "/", "size-histogram.pdf", sep=""), width=10, height=3, scale=1)

# density
p = ggplot(df, aes(x=megabytes, colour=type))
p = p + geom_density() + expand_limits(y = 0)
ggsave(p, file=paste(path_to_output, "size-density.pdf", sep=""), width=10, height=3, scale=1)

###############################################################################
# DURATION
# hist
p = ggplot(df, aes(x=duration))
p = p + geom_histogram(binwidth = 5) + expand_limits(y = 0)
p = p + xlab("duration in seconds")
ggsave(p, file=paste(path_to_output, "/", "duration-histogram.pdf", sep=""), width=10, height=3, scale=1)

# density
p = ggplot(df, aes(x=duration, colour=type))
p = p + geom_density() + expand_limits(y = 0)
p = p + xlab("duration in seconds")
ggsave(p, file=paste(path_to_output, "/", "duration-density.pdf", sep=""), width=10, height=3, scale=1)



###############################################################################
# ??
p = ggplot(mdf, aes(x=duration, value))
p = p + geom_line(aes(color=variable, alpha = 0.25,))
p = p + scale_alpha(guide = 'none')
p = p + ylab("drives")
ggsave(p, file=paste(path_to_output, "/", "drives-timeseries.pdf", sep=""), width=10, height=3, scale=1)

