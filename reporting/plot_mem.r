library(ggplot2) 
library(scales)


# SETTINGS
outfile = "plot_mem"
df30 = read.csv("30-drives-all/mem.log", sep="", header=TRUE)
df60 = read.csv("60-drives-all/mem.log", sep="", header=TRUE)
df75 = read.csv("75-drives-all/mem.log", sep="", header=TRUE)

df30$datetime <- as.POSIXct(strptime(df30$datetime, "%H:%M:%S"))
df60$datetime <- as.POSIXct(strptime(df60$datetime, "%H:%M:%S"))
df75$datetime <- as.POSIXct(strptime(df75$datetime, "%H:%M:%S"))


formatter_mb <- function(x){ 
    x/(1000) 
}


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Plots
p = ggplot(df30, aes(x=datetime, y=value, color=variable)) + scale_y_continuous(labels = formatter_mb) + ylab("megabytes")
p = p + geom_line(aes(y=size, col="size")) 
p = p + geom_line(aes(y=rss, col="rss"))
p = p + xlab("runtime")
ggsave(p, file=paste(outfile, "-usage30.pdf", sep=""), width=4, height=2, scale=1)

p = ggplot(df30, aes(x=datetime, y=value, color=variable)) + scale_y_continuous(labels = formatter_mb) + ylab("megabytes")
p = p + geom_line(aes(y=size, col="size")) 
p = p + geom_line(aes(y=rss, col="rss"))
p = p + xlab("runtime")
ggsave(p, file=paste(outfile, "-usage60.pdf", sep=""), width=4, height=2, scale=1)

p = ggplot(df30, aes(x=datetime, y=value, color=variable)) + scale_y_continuous(labels = formatter_mb) + ylab("megabytes")
p = p + geom_line(aes(y=size, col="size")) 
p = p + geom_line(aes(y=rss, col="rss"))
p = p + xlab("runtime")
ggsave(p, file=paste(outfile, "-usage75.pdf", sep=""), width=4, height=2, scale=1)



p = ggplot(df30, aes(x=datetime, y=value, color=variable)) + scale_y_continuous(labels = formatter_mb) + ylab("megabytes")
p = p + geom_line(aes(y=size, col="size")) 
p = p + geom_line(aes(y=rss, col="rss"))

p = p + geom_line(data=df60, aes(y=size, col="size")) 
p = p + geom_line(data=df60, aes(y=rss, col="rss"))

p = p + geom_line(data=df75, aes(y=size, col="size")) 
p = p + geom_line(data=df75, aes(y=rss, col="rss"))

p = p + xlab("runtime")

#p = p + geom_line(aes(y=vsize, col="vsize")) 
#p = p + geom_line(aes(y=vsz, col="vsz"))
#p = p + theme_bw() 
ggsave(p, file=paste(outfile, "-usage-combined.pdf", sep=""), width=7, height=2, scale=1)



