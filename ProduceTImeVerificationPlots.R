#Note that the pdf has long dashes in the file names

# install.packages("ggplot2")
library(ggplot2)

# Organise data
data <- read.csv("F:/score/score.csv")
data$ColourScore <- as.numeric(data$ColourScore)
data$Folder <- substr(data$SourceFile, 0, nchar(data$SourceFile) - nchar(gsub(".*\\\\", "", data$SourceFile)) - 1)

# Convert to a number of hours with decimals
data$Hour <- as.numeric(substr(data$CreateDate, 11, 13))
data$Minute <- as.numeric(substr(data$CreateDate, 15, 16))
data$Second <- as.numeric(substr(data$CreateDate, 18, 19))
data$Minute <- data$Minute + data$Second/60
data$Hour <- data$Hour + data$Minute/60
data <- data[, 4:7]

#Remove lonely folders
data <- data[data$LonelyFolder == "True",]
# Remove NAs
data <- data[complete.cases(data$ColourScore), ]

# Get counts of internal versus external runs
# dataI <- data[grepl("INTERNAL", data$Folder), ]
# dataI$Folder <- as.factor(dataI$Folder)
# levels(dataI$Folder)
# dataE <- data[!grepl("INTERNAL", data$Folder), ]
# dataE$Folder <- as.factor(dataE$Folder)
# levels(dataE$Folder)
# dataE$Folder <- droplevels(dataE$Folder)


# Open pdf
pdf("C:/Users/petam/Desktop/Chapter 3 current files/suspiciousTimes.pdf")

# Plot graphs
i <- 1
data$Folder <- as.factor(data$Folder)
folder_list <- levels(data$Folder)
while (i <= length(folder_list)) {
  folder_data <- data[data$Folder == folder_list[i], ]
  
  # Plot the graph
  p <- ggplot(data = folder_data, aes(x = Hour, y = ColourScore)) +
    geom_point() +
    geom_vline(xintercept = c(5.5, 21.5), linetype = "dotted", color = "blue", linewidth = 1) +
    geom_vline(xintercept = c(8, 17), linetype = "dotted", color = "red", linewidth = 1) +
    scale_x_continuous(limits = c(0,23), breaks = seq(0, 24, by = 2)) +
    ggtitle(folder_list[i]) +
    theme(plot.title = element_text(size = 5))
  
  # Print the plot to the pdf
  print(p)
  
  i <- i + 1
}

# Close the pdf device
dev.off()

