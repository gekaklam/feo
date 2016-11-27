library(ggplot2) 
library(reshape2)
library(scales)


# SETTINGS
outfile = "plot_snapshot-cache-timeline"
df = read.csv("cache.csv", sep=",", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%Y-%m-%d %H:%M:%S"))




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plots

num_bins = 50000
freqpoly_factor = 5


#limits = c(as.POSIXct("2016-01-17"), as.POSIXct("2016-02-06 01:00:00"))
#weeks <- data.frame(Date=seq(as.POSIXct("2015-12-01"), limits[2], by="weeks"))


p = ggplot(df, aes(x=datetime))
p = p + geom_line(aes(y = bytes_total, colour = "bytes total"))
p = p + geom_line(aes(y = bytes_used, colour = "bytes available"))
#p = p + expand_limits(y=0)
ggsave(p, file=paste(outfile, "-bytes.pdf", sep=""), width=10, height=2, scale=1)


p = ggplot(df, aes(x=datetime))
p = p + geom_line(aes(y = files_total, colour = "files total"))
p = p + geom_line(aes(y = files_dirty, colour = "files dirty"))
ggsave(p, file=paste(outfile, "-files.pdf", sep=""), width=10, height=2, scale=1)


p = ggplot(df, aes(x=datetime))
p = p + geom_line(aes(y = percent_utilization, colour = "% utilization"))
#p = p + expand_limits(y=0)
ggsave(p, file=paste(outfile, "-percent.pdf", sep=""), width=10, height=2, scale=1)





