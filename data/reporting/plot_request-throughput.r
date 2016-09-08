library(ggplot2) 

# read data
df = read.csv("snapshot/requests.csv", header=TRUE)

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
p = ggplot(df, aes(x=throughput))
p = p + geom_density() + expand_limits(y = 0) + continues_x_log10(labels = formatter_byte_to_gb) + xlab("megabytes")
#
## save plot as pdf
ggsave(p, file="generated_plots/plot_request-throughput-density.pdf", width=4, height=2, scale=1)
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
