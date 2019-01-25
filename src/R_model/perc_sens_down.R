# perc_model.R
# Load packages
library(gamlss)

# Fetch command line arguments
myArgs <- commandArgs(trailingOnly = TRUE)

# Convert to numerics
nums = as.numeric(myArgs[1:3])

# cat will write the result to the stdout stream
#cat(myArgs[1:3])

# Load some data
#data = read.csv(myArgs[4], header = TRUE, sep = ";", encoding = "latin1")
data = read.csv(myArgs[4], header = TRUE, sep = ",", encoding = "latin1")

# Configuration
median_df = nums[1]
sigma_df = nums[2]
nu_df = nums[3]

points_on = myArgs[7]
#res = 100

#gesch = myArgs[7]
#gesch_n = myArgs[8]
graph_title = myArgs[6]

# x_label = myArgs[8]
# y_label = myArgs[9]

x_label = myArgs[5]
y_label = myArgs[6]

x_axis = make.names(myArgs[5])
y_axis = make.names(myArgs[6])

# xlim1 = as.numeric(myArgs[10])
# xlim2 = as.numeric(myArgs[11])
# xsteps = as.numeric(myArgs[12])
# 
# ylim1 = as.numeric(myArgs[13])
# ylim2 = as.numeric(myArgs[14])
# ysteps = as.numeric(myArgs[15])
# 
# x_axis = myArgs[5]
# y_axis = myArgs[6]

# Percentiles

#auf mac hats funktioniert:
#data_perc <- data_filtered %>% select(x_axis, y_axis)
####

data_perc_1 <- data.frame(data[,x_axis],data[,y_axis])

colnames(data_perc_1)[1] = "x"
colnames(data_perc_1)[2] = "y"

data_perc<-na.omit(data_perc_1)

xsteps = (max(data_perc$x) - min(data_perc$x))/10
xlim1 = min(data_perc$x) - xsteps
xlim2 = max(data_perc$x) + xsteps

ysteps = (max(data_perc$y) - min(data_perc$y))/10
ylim1 = min(data_perc$y) - ysteps
ylim2 = max(data_perc$y) + ysteps

m1 <- gamlss(y ~ pb(x, df = median_df),
             sigma.formula = ~ pb(x, df = sigma_df),
             nu.formula = ~pb(x, df = nu_df),
             family = "BCCG",
             method = RS(),
             data = data_perc)

summary(m1)

# label_perc <- centiles.pred(m1, xvalues=max(data_perc$x), xname= "x", cent = c(3, 10, 25, 50, 75, 90, 97))
# 
# png("./tmp_sens/percentiles_down.png")
# centiles(m1,
#          xvar = data_perc$x,
#          ylim = c(ylim1,ylim2),
#          xlim = c(xlim1,xlim2),
#          legend = FALSE,col=1,col.cent=1,
#          cent = c(3, 10, 25, 50, 75, 90, 97),
#          lwd.cent=c(1,1,1,2,1,1,1),
#          main=graph_title,
#          xlab = "",
#          ylab = "",
#          labels = TRUE,
#          axes=TRUE,
#          points = points_on)
#          #tck = FALSE,
#          #xaxs="i",
#          #yaxs="i")
# 
# 
# title(ylab = y_label, line=2.2)
# title(xlab = x_label, line=2.2)
# #axis(1, at = seq(xlim1, xlim2, by=xsteps), labels = seq(xlim1, xlim2, by=xsteps),tck = -0.01, cex.axis=0.8,mgp=c(0,0.2,0))
# abline(h= seq(ylim1, ylim2, by=ysteps), v=seq(xlim1, xlim2, by=xsteps), col="gray", lty=3)
# #print(ysteps)
# #print(str(ysteps))
# #axis(2, at = seq(ylim1, ylim2, by=ysteps), labels = seq(ylim1, ylim2, by=ysteps),tck = -0.01, cex.axis=1,las=2,mgp=c(0,0.4,0))
# text(1.05*max(data_perc$x), label_perc$C3, "P3", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C10, "P10", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C25, "P25", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C50, "P50", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C75, "P75", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C90, "P90", cex = 0.7)
# text(1.05*max(data_perc$x), label_perc$C97, "P97", cex = 0.7)
# 
# dev.off()


x_values <- seq(round(min(data_perc$x),1), round(max(data_perc$x),1), length.out = 100)

lms_values <- predictAll(m1, newdata=data.frame(x=x_values))
centile_values <- centiles.pred(m1, xname="x", xvalues=x_values, cent = c(3, 10, 25, 50, 75, 90, 97))

chart <- data.frame(lms_values, centile_values)
write.csv(chart, file = paste(dirname(dirname(myArgs[4])),"/tmp_sens/percentiles_chart_down.csv", sep=""))