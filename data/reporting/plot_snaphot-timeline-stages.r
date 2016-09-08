library(ggplot2) 
library(scales)


# SETTINGS
outfile = "generated_plots/plot_snapshot-stages-timeline"
df = read.csv("snapshot/stages.csv", sep=",", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%Y-%m-%d %H:%M:%S"))




# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plots

num_bins = 50000
freqpoly_factor = 5


limits = c(as.POSIXct("2016-01-17"), as.POSIXct("2016-02-06 01:00:00"))
weeks <- data.frame(Date=seq(as.POSIXct("2015-12-01"), limits[2], by="weeks"))

p = ggplot(df, aes(x=datetime, y=count))
p = p + geom_line(colour='red')  + ylab("Stages")
#p = p + geom_histogram(bins=num_bins/5) + xlab(NULL) + ylim(0, 60)
#p = p + scale_x_datetime(breaks = date_breaks("2 days"), 
#			 labels = date_format("%a")
#	)

#p = p + scale_x_datetime(breaks = date_breaks("2 days"), 
#			 labels = date_format("%a"),
#			 limits = limits
#	)

p = p + geom_vline(data=weeks, xintercept=as.numeric(weeks$Date), linetype="longdash", size=0.2, alpha=0.5)
#p = p + theme(legend.position="bottom")
#p = p + theme_bw() 
ggsave(p, file=paste(outfile, "-full.pdf", sep=""), width=10, height=3, scale=1)




# limited case
p = ggplot(df, aes(x=datetime, y=count))
p = p + geom_line(colour='red') 
p = p + xlab(NULL) + ylim(0, 60) + ylab("Stages")
p = p + scale_x_datetime(breaks = date_breaks("2 days"), 
			 labels = date_format("%a"),
			 limits = limits
	)

p = p + geom_vline(data=weeks, xintercept=as.numeric(weeks$Date), linetype="longdash", size=0.2, alpha=0.5)
#p = p + theme(legend.position="bottom")
#p = p + theme_bw() 
ggsave(p, file=paste(outfile, "-limited.pdf", sep=""), width=10, height=3, scale=1)




