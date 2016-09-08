library(ggplot2) 
library(plyr)


# read data
df = read.csv("snapshot/waiting.csv", sep=",", header=TRUE)

drops <- c("count")
df = df[ , !(names(df) %in% drops)]

dfsum = as.data.frame(colSums(df[,-1]))

row.names(dfsum) = c("< 1m","< 2m","< 3m","< 4m","< 5m","< 8m","< 10m","< 15m","< 20m","< 30m","< 1h","< 2h","< 4h","< 8h", "more")


dfsum$name = row.names(dfsum)
dfsum$name = factor(dfsum$name, levels=dfsum$name)

names(dfsum)[names(dfsum)=="colSums(df[, -1])"] <- "count"


p = ggplot(data=dfsum, aes(x=name,y=count/sum(count))) + geom_bar(stat="identity") + ylab("Jobs") + xlab("total wait-times") + ylim(0,1)
ggsave(p, file="generated_plots/plot_wait-times.pdf", width=7, height=1.5, scale=1)


p = ggplot(data=dfsum, aes(x=name,y=cumsum(count/sum(count)))) + geom_bar(stat="identity") + ylab("Jobs") + xlab("total wait-times") + ylim(0,1)
ggsave(p, file="generated_plots/plot_wait-times-cum.pdf", width=7, height=1.5, scale=1)

