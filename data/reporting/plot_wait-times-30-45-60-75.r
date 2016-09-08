library(ggplot2) 
library(plyr)


# read data
df30 = read.csv("30-drives-all/2016-03-05T19:09:32.975267_7dea5acfbd/waiting.csv", sep=",", header=TRUE)
df45 = read.csv("45-drives-all/2016-03-06T14:17:53.445848_6c7c5d6b9d/waiting.csv", sep=",", header=TRUE)
df60 = read.csv("60-drives-all/2016-03-06T09:56:30.834479_31bc2318d8/waiting.csv", sep=",", header=TRUE)
df75 = read.csv("75-drives-all/2016-03-05T21:46:01.138955_4b210ec009/waiting.csv", sep=",", header=TRUE)


drops <- c("count")
df30 = df30[ , !(names(df30) %in% drops)]
df45 = df45[ , !(names(df45) %in% drops)]
df60 = df60[ , !(names(df60) %in% drops)]
df75 = df75[ , !(names(df75) %in% drops)]

df30sum = as.data.frame(colSums(df30[,-1]))
df45sum = as.data.frame(colSums(df45[,-1]))
df60sum = as.data.frame(colSums(df60[,-1]))
df75sum = as.data.frame(colSums(df75[,-1]))

row.names(df30sum) = c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more")
row.names(df45sum) = c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more")
row.names(df60sum) = c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more")
row.names(df75sum) = c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more")

df30sum$name = row.names(df30sum)
df30sum$name = factor(df30sum$name, levels=df30sum$name)

df45sum$name = row.names(df45sum)
df45sum$name = factor(df45sum$name, levels=df45sum$name)

df60sum$name = row.names(df60sum)
df60sum$name = factor(df60sum$name, levels=df60sum$name)

df75sum$name = row.names(df75sum)
df75sum$name = factor(df75sum$name, levels=df75sum$name)


#rename(df30sum, c("colSums(df30[, -1])"="count"))
#rename(df60sum, c("colSums(df60[, -1])"="count"))
#rename(df75sum, c("colSums(df75[, -1])"="count"))

names(df30sum)[names(df30sum)=="colSums(df30[, -1])"] <- "count"
names(df45sum)[names(df45sum)=="colSums(df45[, -1])"] <- "count"
names(df60sum)[names(df60sum)=="colSums(df60[, -1])"] <- "count"
names(df75sum)[names(df75sum)=="colSums(df75[, -1])"] <- "count"



myxlabel = "total wait-times"


p = ggplot(data=df30sum, aes(x=name,y=count/sum(count))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-30.pdf", width=7, height=1.5, scale=1)


p = ggplot(data=df45sum, aes(x=name,y=count/sum(count))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-45.pdf", width=7, height=1.5, scale=1)

p = ggplot(data=df60sum, aes(x=name,y=count/sum(count))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-60.pdf", width=7, height=1.5, scale=1)

p = ggplot(data=df75sum, aes(x=name,y=count/sum(count))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-75.pdf", width=7, height=1.5, scale=1)




p = ggplot(data=df30sum, aes(x=name,y=cumsum(count/sum(count)))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-30-cum.pdf", width=7, height=1.5, scale=1)

p = ggplot(data=df45sum, aes(x=name,y=cumsum(count/sum(count)))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-45-cum.pdf", width=7, height=1.5, scale=1)

p = ggplot(data=df60sum, aes(x=name,y=cumsum(count/sum(count)))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-60-cum.pdf", width=7, height=1.5, scale=1)

p = ggplot(data=df75sum, aes(x=name,y=cumsum(count/sum(count)))) + geom_bar(stat="identity") + ylab("Jobs") + xlab(myxlabel) + ylim(0,1)
ggsave(p, file="plot_wait-times-75-cum.pdf", width=7, height=1.5, scale=1)


# create boxplot, start y from 0
#p = ggplot(df, aes(factor(type), throughput))
#p = p + geom_boxplot() + geom_jitter() + expand_limits(y = 0)

# save plot as pdf
#ggsave(p, file="generated_plots/plot_request-throughput.pdf", width=2, height=4, scale=1)




formatter_byte_to_gb <- function(x){ 
    x/(1000*1000*1000) 
}


## DENSITY
# create boxplot, start y from 0
#p = ggplot(df, aes(x=throughput))
#p = p + geom_density() + expand_limits(y = 0) + continues_x_log10(labels = formatter_byte_to_gb) + xlab("megabytes")
#
## save plot as pdf
#ggsave(p, file="plot_request-wait-times-density-75.pdf", width=4, height=2, scale=1)


#
#
## HISTOGRAM
## create boxplot, start y from 0
#p = ggplot(df, aes(x=throughput))
#p = p + geom_histogram() + expand_limits(y = 0)
#
## save plot as pdf
#ggsave(p, file="generated_plots/plot_request-throughput-histogram.pdf", width=4, height=2, scale=1)
#
#
## HISTOGRAM
## create boxplot, start y from 0
#p = ggplot(df, aes(x=throughput))
#p = p + geom_histogram() + geom_density() + expand_limits(y = 0)
#
## save plot as pdf
#ggsave(p, file="generated_plots/plot_request-throughput-histogram+density.pdf", width=4, height=2, scale=1)
#
