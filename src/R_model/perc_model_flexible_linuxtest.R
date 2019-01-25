# perc_model_flexible.R

zz <- file("/R_model/log_model_fitting.Rout", open="wt")
sink(zz, type="message")

# Load packages
library(gamlss)

#Rscript '/home/chris/Desktop/refcurv_0.4.1_linux/src/R_model/perc_model_flexible.R'  
#'1' '0', '0' '/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv' 
#'age [month]' 'EDV [ml]' 'TRUE' 'gamlss(y ~ pb(x, df = median_df), sigma.formula = ~ pb(x, df = sigma_df), nu.formula = ~pb(x, df = nu_df), family = "BCCG", method = RS(), data = data_perc)'


# Fetch command line arguments
myArgs <- commandArgs(trailingOnly = TRUE)

# Convert to numerics
#nums = as.numeric(myArgs[1:3])

# Load data
data = read.csv('/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv', header = TRUE, sep = ",", encoding = "latin1")

# Configuration edf for L, M and S
median_df = 1
sigma_df = 0
nu_df = 0

# points on or off
points_on = 'TRUE'

# graph title
graph_title = 'EDV [ml]'

# axis label
x_label = 'age [month]'
y_label = 'ESV [ml]'

x_axis = make.names('age [month]')
y_axis = make.names('ESV [ml]')

# data preparation steps
data_perc_1 <- data.frame(data[,x_axis],data[,y_axis])

colnames(data_perc_1)[1] = "x"
colnames(data_perc_1)[2] = "y"

data_perc<-na.omit(data_perc_1)

# limits
xsteps = (max(data_perc$x) - min(data_perc$x))/10
xlim1 = min(data_perc$x) - xsteps
xlim2 = max(data_perc$x) + xsteps

ysteps = (max(data_perc$y) - min(data_perc$y))/10
ylim1 = min(data_perc$y) - ysteps
ylim2 = max(data_perc$y) + ysteps

# text output
print('gamlss(y ~ pb(x, df = median_df), sigma.formula = ~ pb(x, df = sigma_df), nu.formula = ~pb(x, df = nu_df), family = "BCCG", method = RS(), data = data_perc)')
print(paste(dirname('/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv' ),"/percentiles.png", sep=""))
m1 <- eval(parse(text = 'gamlss(y ~ pb(x, df = median_df), sigma.formula = ~ pb(x, df = sigma_df), nu.formula = ~pb(x, df = nu_df), family = "BCCG", method = RS(), data = data_perc)'))
summary(m1)

# label setting
label_perc <- centiles.pred(m1, xvalues=max(data_perc$x), xname= "x", cent = c(3, 10, 25, 50, 75, 90, 97))

# create png
png(paste(dirname('/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv' ),"/percentiles.png", sep=""))
centiles(m1,
         xvar = data_perc$x,
         ylim = c(ylim1,ylim2),
         xlim = c(xlim1,xlim2),
         legend = FALSE,col=1,col.cent=1,
         cent = c(3, 10, 25, 50, 75, 90, 97),
         lwd.cent=c(1,1,1,2,1,1,1),
         main=graph_title,
         xlab = "",
         ylab = "",
         labels = TRUE,
         axes=TRUE,
         points = points_on)



title(ylab = y_label, line=2.2)
title(xlab = x_label, line=2.2)
abline(h= seq(ylim1, ylim2, by=ysteps), v=seq(xlim1, xlim2, by=xsteps), col="gray", lty=3)

text(1.05*max(data_perc$x), label_perc$C3, "P3", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C10, "P10", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C25, "P25", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C50, "P50", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C75, "P75", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C90, "P90", cex = 0.7)
text(1.05*max(data_perc$x), label_perc$C97, "P97", cex = 0.7)

dev.off()

# LMS Chart
# x values for chart
x_values <- seq(round(min(data_perc$x),1), round(max(data_perc$x),1), length.out = 100)

# LMS values
lms_values <- predictAll(m1, newdata=data.frame(x=x_values))
# percentile values
centile_values <- centiles.pred(m1, xname="x", xvalues=x_values, cent = c(3, 10, 25, 50, 75, 90, 97))

# residuals
resid_m1 <- centiles.pred(m1, xname="x", xvalues=data_perc$x, yval=data_perc$y, type="z-scores")

# saving
chart <- data.frame(lms_values, centile_values)
write.csv(chart, file = paste(dirname('/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv' ),"/percentiles_chart.csv", sep=""))

res_chart <- data.frame(resid_m1)
write.csv(res_chart, file = paste(dirname('/home/chris/Desktop/refcurv_0.4.1_linux/src/tmp/cur_data.csv' ),"/res_chart.csv", sep=""))
#sink(type="message")
#close(zz)
