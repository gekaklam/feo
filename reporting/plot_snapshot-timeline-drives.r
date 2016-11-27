library(ggplot2) 
library(scales)


# SETTINGS
outfile = "plot_snapshot-drives-timeline"
df = read.csv("drives.csv", sep=",", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%Y-%m-%d %H:%M:%S"))




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plots

num_bins = 50000
freqpoly_factor = 5


#limits = c(as.POSIXct("2016-01-17"), as.POSIXct("2016-02-06 01:00:00"))
#weeks <- data.frame(Date=seq(as.POSIXct("2015-12-01"), limits[2], by="weeks"))

p = ggplot(df, aes(x=datetime))
p = p + geom_line(aes(y = total, colour = "total"))
p = p + geom_line(aes(y = free, colour = "enabled"))
p = p + geom_line(aes(y = enabled, colour = "free"))
p = p + expand_limits(y=0)

ggsave(p, file=paste(outfile, "-full.pdf", sep=""), width=10, height=2, scale=1)




