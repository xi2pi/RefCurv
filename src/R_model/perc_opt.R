# perc_opt.R
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

x_axis = make.names(myArgs[5])
y_axis = make.names(myArgs[6])

data_perc_1 <- data.frame(data[,x_axis],data[,y_axis])

colnames(data_perc_1)[1] = "x"
colnames(data_perc_1)[2] = "y"

data_perc<-na.omit(data_perc_1)

result = tryCatch({
m1 <- gamlss(y ~ pb(x, df = median_df),
             sigma.formula = ~ pb(x, df = sigma_df),
             nu.formula = ~pb(x, df = nu_df),
             family = "BCCG",
             method = RS(),
             data = data_perc,
             control=gamlss.control(trace=FALSE))
#summary(m1)

res <- m1$sbc
}, error = function(e) {
res <- "-"
})

print(result)

