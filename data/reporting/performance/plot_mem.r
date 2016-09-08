library(ggplot2) 
library(scales)


# SETTINGS
outfile = "generated_plots/plot_mem"
df = read.csv("mem.log", sep="", header=TRUE)
df$datetime <- as.POSIXct(strptime(df$datetime, "%H:%M:%S"))



formatter_mb <- function(x){ 
    x/(1000) 
}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plots
p = ggplot(df, aes(x=datetime, y=value, color=variable)) + scale_y_continuous(labels = formatter_mb) + ylab("megabytes")
p = p + geom_line(aes(y=size, col="size")) 
#p = p + geom_line(aes(y=vsize, col="vsize")) 
p = p + geom_line(aes(y=rss, col="rss"))
#p = p + geom_line(aes(y=vsz, col="vsz"))
#p = p + theme_bw() 
ggsave(p, file=paste(outfile, "-usage.pdf", sep=""), width=5, height=2, scale=1)



