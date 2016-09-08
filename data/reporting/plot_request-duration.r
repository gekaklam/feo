library(ggplot2) 

# read data
df = read.csv("snapshot/requests.csv", header=TRUE)

# create boxplot, start y from 0
#p = ggplot(df, aes(factor(type), duration))
#p = p + geom_boxplot() + geom_jitter() + expand_limits(y = 0)

# save plot as pdf
#ggsave(p, file="generated_plots/plot_request-duration.pdf", width=2.75, height=4, scale=1)




## DENSITY
## create boxplot, start y from 0
p = ggplot(df, aes(x=duration))
p = p + geom_density() + expand_limits(y = 0)

## save plot as pdf
ggsave(p, file="generated_plots/plot_request-duration-density.pdf", width=4, height=2, scale=1)


## HISTOGRAM
## create boxplot, start y from 0
#p = ggplot(df, aes(x=duration))
#p = p + geom_histogram() + expand_limits(y = 0)

## save plot as pdf
#ggsave(p, file="generated_plots/plot_request-duration-histogram.pdf", width=4, height=2, scale=1)





