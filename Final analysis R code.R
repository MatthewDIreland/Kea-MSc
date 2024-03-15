
library(ggplot2)
library(tidyr)
library(dplyr)

#######################################################################################
# Make table showing length of sessions for different species
#######################################################################################

input_data <- read.csv("C:/Users/petam/Desktop/Critical files/TaggingOfPredatorSessionsRemoveDuplicateBoth.csv")
data_sessions <- input_data
data_sessions$SessionCode <- substr(data_sessions$File, 1, 4)
data_sessions$Camera <- ifelse(grepl("INTERNAL", data_sessions$OriginalFile), "INTERNAL", "EXTERNAL")
data_sessions <- data_sessions %>%
  mutate(ActualCode = sub("^(\\D*\\d+_).*", "\\1", File))
data_sessions <- data_sessions[,c(6,11,13,14)]
data_sessions <- as.data.frame(table(data_sessions))
data_sessions <- data_sessions[data_sessions$Freq != 0, ]
# Remove empty sessions and duplicate entries for sessions that were not empty but contained an empty image
data_sessions <- data_sessions[data_sessions$NewAnimalTag != "empty", ]
# Get all sessions containing multiple animals
removed_sessions <- data_sessions[duplicated(data_sessions$ActualCode) | duplicated(data_sessions$ActualCode, fromLast = TRUE), ]
removed_sessions <- removed_sessions[,-c(2,5)]
removed_sessions$ActualCode <- rep(c(1:2),times = 51)

# Get all sessions without multiple animals
data_sessions <- data_sessions[!(duplicated(data_sessions$ActualCode) | duplicated(data_sessions$ActualCode, fromLast = TRUE)), ]
data_sessions <- data_sessions[,c(1:4)]
data_sessions$SessionDurationSeconds <- as.numeric(data_sessions$SessionDurationSeconds)

data_sessions <- data_sessions %>%
  group_by(NewAnimalTag, Camera) %>%
  summarise(
    Sum = sum(SessionDurationSeconds),
    Count = n(),
    Mean = mean(SessionDurationSeconds),
    Median = median(SessionDurationSeconds),
    SD = sd(SessionDurationSeconds),
    Min = min(SessionDurationSeconds),
    Max = max(SessionDurationSeconds),
    Q1 = quantile(SessionDurationSeconds, 0.25),
    Q3 = quantile(SessionDurationSeconds, 0.75)
  )

# data_sessions <- data_sessions[data_sessions$NewAnimalTag != "kea", ]

############################################################################################




########################################################################################
# Make table showing length of sessions for different species
# No matter how I tried to present this as a bar plot or box and whiskers it didnt work
#######################################################################################
# input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
# sessions_data <- subset(input_data, grepl(paste0("^", "SessionFirstAndMax"), input_data$RelativePath))
# sessions_data <- subset(sessions_data, grepl(paste0("^", "Max"), sessions_data$PhotoSource))
# sessions_data <- sessions_data[,c(6,11,15)]
# sessions_data$Camera <- ifelse(grepl("INTERNAL", sessions_data$OriginalFile), "INTERNAL", "EXTERNAL")
# sessions_data <- sessions_data[,-2]
# 
# sessions_data <- sessions_data %>%
#   group_by(Animal, Camera) %>%
#   summarise(
#     Sum = sum(SessionDurationSeconds),
#     Count = n(),
#     Mean = mean(SessionDurationSeconds),
#     Median = median(SessionDurationSeconds),
#     SD = sd(SessionDurationSeconds),
#     Min = min(SessionDurationSeconds),
#     Max = max(SessionDurationSeconds),
#     Q1 = quantile(SessionDurationSeconds, 0.25),
#     Q3 = quantile(SessionDurationSeconds, 0.75)
#   )

########################################################################################
# Make table comparing session selection criteria
#######################################################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
new_data <- subset(input_data, grepl(paste0("^", "SessionFirstAndMax"), input_data$RelativePath))
new_data_first <- new_data[,c(6,10)]
new_data_first <- subset(new_data_first, grepl(paste0("^", "First"), new_data_first$PhotoSource))
new_data_first_table <- as.data.frame(table(new_data_first))
new_data_max <- new_data[,c(6,10)]
new_data_max <- subset(new_data_max, grepl(paste0("^", "Max"), new_data_max$PhotoSource))
new_data_max_table <- as.data.frame(table(new_data_max))
new_data_agreement <- cbind(new_data_first, new_data_max)

colnames(new_data_agreement) <- c("Animal1", "PhotoSource", "Animal2", "PhotoSource")
new_data_agreement <- new_data_agreement[new_data_agreement$Animal1 == new_data_agreement$Animal2, ]
new_data_agreement <- new_data_agreement[,1]
agreement_table <- as.data.frame(table(new_data_agreement))
both_table <- cbind(new_data_first_table, new_data_max_table, agreement_table)
both_table <- both_table[,c(1,3,6,8)]
colnames(both_table) <- c("Animal","FirstPhotoTag","MaxPhotoTag","SharedSessions")


###################################################################################
# Make a table showing accuracy for each class given by AI. Split by internal external
##################################################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
accuracy_data <- subset(input_data, grepl(paste0("^", "SessionFirstAndMax"), input_data$RelativePath))
accuracy_data <- subset(accuracy_data, grepl(paste0("^", "Max"), accuracy_data$PhotoSource))
accuracy_data$AI_tag <- gsub('nz_falcon', 'falcon', accuracy_data$AI_tag)
accuracy_data$Position <- substr(accuracy_data$RelativePath, nchar(accuracy_data$RelativePath) - 7, nchar(accuracy_data$RelativePath))
accuracy_data$Status <- accuracy_data$Animal == accuracy_data$AI_tag
accuracy_data <- accuracy_data[,c(6,17,18)]
accuracy_table <- as.data.frame(table(accuracy_data))
accuracy_table_TRUE <- accuracy_table[accuracy_table$Status == "TRUE", ]
accuracy_table_FALSE <- accuracy_table[accuracy_table$Status == "FALSE", ]
accuracy_table <- cbind(accuracy_table_TRUE, accuracy_table_FALSE)
accuracy_table <- accuracy_table[,-c(3,5,6,7)]
colnames(accuracy_table) <- c("Animal","Position","TotalCorrect","TotalIncorrect")
accuracy_table$Accuracy <- trunc(100*(accuracy_table$TotalCorrect/(accuracy_table$TotalCorrect + accuracy_table$TotalIncorrect)))
accuracy_table <- accuracy_table[accuracy_table$Animal != "unknown animal", ]
accuracy_table <- accuracy_table[accuracy_table$Animal != "other animal", ]


###############################################################
# Make a confusion matrix
############################################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
confusion_matrix <- subset(input_data, grepl(paste0("^", "SessionFirstAndMax"), input_data$RelativePath))
confusion_matrix <- subset(confusion_matrix, grepl(paste0("^", "Max"), confusion_matrix$PhotoSource))
confusion_matrix <- confusion_matrix[,c(6,9)]
confusion_matrix <- as.data.frame(table(confusion_matrix))
confusion_matrix <- as.data.frame(reshape(confusion_matrix, idvar = "AI_tag", timevar = "Animal", direction = "wide"))
#Shows all potential tags:
tags_data <- read.csv("C:/Users/petam/Desktop/Critical files/ImageData.csv")
levels(as.factor(tags_data$Label))

#################################################################################################
# Calculate how often an "empty" session is genuinely empty
############################################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
empty_sessions_Max <- subset(input_data, grepl(paste0("^", "SampleEmptyMaxSessions"), input_data$RelativePath))
empty_sessions_Max <- empty_sessions_Max[,c(3,6)]
# These two lines make a table and removes empty data added by R
# This table has 119 entries, meaning there are at least 19 sessions with multiple different tags
empty_session_max_table <- as.data.frame(table(empty_sessions_Max))
empty_session_max_table <- empty_session_max_table[empty_session_max_table$Freq != 0, ]
# The table below has only sessions that have a single tag the entire time 
# There are 81 of these. This means that 19 have multiple tags. 1 of these 81 is also not "empty" but all tags should be empty in this data
#As such the number of sessions that were thought to be empty where a animal was actually present in one of the photos is 
# 19 + 1 = 20 sessions
pure_sessions <- subset(empty_session_max_table, !(duplicated(RelativePath) | duplicated(RelativePath, fromLast = TRUE)))
###############################################
empty_sessions_First <- subset(input_data, grepl(paste0("^", "SampleEmptyFirstSessions"), input_data$RelativePath))
empty_sessions_First <- empty_sessions_First[,c(3,6)]
# These two lines make a table and removes empty data added by R
# This table has 147 entries, meaning there are at least 47 sessions with multiple different tags
empty_session_first_table <- as.data.frame(table(empty_sessions_First))
empty_session_first_table <- empty_session_first_table[empty_session_first_table$Freq != 0, ]
# The table below has only sessions that have a single tag the entire time 
# There are 56 of these. This means that 44 have multiple tags. 1 of these 44 is also not "empty" but all tags should be empty in this data
#As such the number of sessions that were thought to be empty where a animal was actually present in one of the photos is 
# 44 + 1 = 45 sessions
pure_sessions <- subset(empty_session_first_table, !(duplicated(RelativePath) | duplicated(RelativePath, fromLast = TRUE)))


#############################################################################
# Calculates how often there are multiple animals in a session
#################################################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
multiple_animals <- subset(input_data, grepl(paste0("^", "SampleSessions"), input_data$RelativePath))
multiple_animals <- multiple_animals[,c(3,6)]
animal_table <- as.data.frame(table(multiple_animals))
animal_table <- animal_table[animal_table$Freq != 0, ]
animal_table <- animal_table[animal_table$Animal != "empty", ]
animal_table <- animal_table[animal_table$Animal != "unknown animal", ]
# Finds sessions where multiple animals have been tagged
animal_not_unique <- subset(animal_table,duplicated(RelativePath) | duplicated(RelativePath, fromLast=TRUE))
#Manual review of the photos here fins only one had multiple animals in the same session: 1 was a person + a kea
#Others had a tagging error
#So of a sample of 100 sessions 0% had multiple species in the different photos from the same sessions


#############################################################################################
#Calculates tagging recall aka intra-observer agreement
#############################################################################################################
# 98% recall, upon review both discrepancies involved 2 photos of kea under extremely low light being tagged as empty, both in the first tagging run.
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/TaggingRecallSample.csv")
recall_stats <- input_data[input_data$Animal != input_data$RecallTag,]


#####################################################################################################
# Compares the performance of Acorn and Browning camera models
###############################################################################################
# Makes a table showing how many triggers are empty in all 3 images
# This is 4 images for the browning of 1590 and 20 images for the acorn of 860
trigger_data <- read.csv("C:/Users/petam/Desktop/Chapter 3 current files/Folders for asessing triggers/Sample folder from COBB (A 27_06_2022_to_22_07_2022)/TriggerTags.csv")
trigger_data$TriggerNo <- rep(1:3, length.out = nrow(trigger_data))
trigger_data$Presence <- ifelse(trigger_data$Animal == "empty", FALSE, TRUE)
empty_data <- trigger_data[c(trigger_data$Presence == "FALSE"),]
empty_data <- empty_data[,c(4,5,7)]
empty_table <- as.data.frame(table(empty_data))
empty_table <- empty_table[c(empty_table$Freq == 3),]
###Calculates the same thing on the individual photo level for photo of all triggers
trigger_data <- read.csv("C:/Users/petam/Desktop/Chapter 3 current files/Folders for asessing triggers/Sample folder from COBB (A 27_06_2022_to_22_07_2022)/TriggerTags.csv")
trigger_data$TriggerNo <- rep(1:3, length.out = nrow(trigger_data))
trigger_data$Presence <- ifelse(trigger_data$Animal == "empty", FALSE, TRUE)
trigger_data <- trigger_data[,c(5,6,7)]
trigger_table <- as.data.frame(table(trigger_data))
trigger_table_a <- trigger_table[trigger_table$Camera == "Acorn",]
trigger_table_b <- trigger_table[trigger_table$Camera == "Browning",]
trigger_table <- as.data.frame(cbind(trigger_table_a$TriggerNo,trigger_table_a$Presence,trigger_table_a$Freq, trigger_table_b$Freq))
colnames(trigger_table) <- c("TriggerNo","Presence","Acorn","Browning")
trigger_table <- pivot_wider(trigger_table, names_from = "Presence", values_from = c("Acorn","Browning"))
trigger_table <- as.data.frame(rbind(trigger_table, c("All", 20, 840, 4, 1586)))
colnames(trigger_table) <- c("TriggerNo","AcornEmpty","AcornNonEmpty","BrowningEmpty", "BrowningNonEmpty")


##################################################################################
# Creates table of AI classification accuracy
##############################################################
input_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
new_data <- subset(input_data, grepl(paste0("^", "SessionFirstAndMax"), input_data$RelativePath))
new_data <- new_data[new_data$PhotoSource == "Max",]
session_classification_accuracy_data <- new_data[,c(6,9,11)]
colnames(session_classification_accuracy_data) <- c("Manual_tag", "AI_tag", "Match")
session_internal <- session_classification_accuracy_data[grepl("INTERNAL", session_classification_accuracy_data$Match), ]
session_internal$Camera <- "INTERNAL"
row.names(session_internal) <- NULL
session_external <- session_classification_accuracy_data[!grepl("INTERNAL", session_classification_accuracy_data$Match), ]
session_external$Camera <- "EXTERNAL"
row.names(session_external) <- NULL
session_classification_accuracy_data <- rbind(session_internal,session_external)
session_classification_accuracy_data <- session_classification_accuracy_data[,-3]
session_classification_accuracy_data$Matching <- session_classification_accuracy_data$Manual_tag == session_classification_accuracy_data$AI_tag
session_classification_accuracy_data$AI_tag <- ifelse(session_classification_accuracy_data$AI_tag == "nz_falcon", "falcon", session_classification_accuracy_data$AI_tag)
session_classification_accuracy_data <- session_classification_accuracy_data[,-2]
session_table <- as.data.frame(table(session_classification_accuracy_data))



#########################################################################
# Make table of activity by month and burrow
#########################################################################
all_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
all_data <- all_data[grepl("MaxSessionPhotos", all_data$File), ]
# make master table
all_table <- all_data
all_table$Camera <- ifelse(grepl("INTERNAL", all_table$OriginalFile), "INTERNAL", "EXTERNAL")
all_table$Month <- substr(all_table$FirstPhotoNZST, 6, 7)
all_table$Burrow <- vapply(strsplit(all_table$OriginalFile, '\\\\'), function(x)
  paste(x[seq.int(4)], collapse='\\\\'), character(1L))
all_table <- all_table[,c(6,17,18,19)]
all_table <- as.data.frame(table(all_table))
all_table <- pivot_wider(all_table, names_from = "Burrow", values_from = "Freq")
#### INTERNAL
############# Get day totals and make into a dataframe to allow dataframes to be divided
burrow_internal <- all_table[grepl("INTERNAL", all_table$Camera), ]
burrow_internal[, sapply(burrow_internal, function(col) all(col == 0))] <- NA
for_table_int <- burrow_internal
for_table_int$TotalInternal <- rowSums(for_table_int[, 4:22], na.rm = TRUE)
# ##################################################################
## EXTERNAL
burrow_external <- all_table[grepl("EXTERNAL", all_table$Camera), ]
burrow_external[, sapply(burrow_external, function(col) all(col == 0))] <- NA
for_table_ext <- burrow_external
for_table_ext$TotalExternal <- rowSums(for_table_ext[, 4:22], na.rm = TRUE)
#########
monthly_activity <- cbind(for_table_int[,c(1,3,23)], for_table_ext[,c(23)])
monthly_activity$Month <- as.numeric(as.character(monthly_activity$Month))



#########################################################################################################
# Create graphs of the average activity at a burrow across all hours of the day, (adjusted by unequal monitoring effort for standardization).
########################################################################################################
all_data <- read.csv("C:/Users/petam/Desktop/Critical files/NEW_ALL_DATA_tagging.csv")
all_data <- all_data[grepl("MaxSessionPhotos", all_data$File), ]

# Adjust times of suspicious folders to be correct (assuming set up occurs in the morning)
data_subset_1 <- all_data[grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2a~_STA26_Raglans\\\\05_08_2020_to_1_09_2020\\\\straight_browning1_photo_05_08_2020_to", all_data$OriginalFile), ]
data_subset_2 <- all_data[grepl("K:\\\\Nelson Lakes\\\\2022-2023\\\\Nest4~St_Ronans\\\\Cavity4a~\\\\D 11_10_2022_to_31_10_2022\\\\Period ending 31_10_22_browning_right_photo", all_data$OriginalFile), ]
#internal
data_subset_3 <- all_data[grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2b~_STA39_Raglans\\\\INTERNAL\\\\internal_browning_photo 03_12_2020_to_19_02_2020\\\\nest", all_data$OriginalFile), ]
data_subset_4 <- all_data[grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2a~_STA26_Raglans\\\\INTERNAL\\\\10_10_2020_to_16_10_2020\\\\internal_borwning1 Photo 10_10_2020_to", all_data$OriginalFile), ]
data_subset <- as.data.frame(rbind(data_subset_1, data_subset_2, data_subset_3, data_subset_4))

# install.packages("lubridate")
library(lubridate)
data_subset$FirstPhotoNZST <- ymd_hms(data_subset$FirstPhotoNZST)  # Convert to POSIXct format if not already
data_subset$FirstPhotoNZST <- data_subset$FirstPhotoNZST + hours(12)
data_subset$FirstPhotoNZST <- as.character(data_subset$FirstPhotoNZST)
less_data <- all_data[!grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2a~_STA26_Raglans\\\\05_08_2020_to_1_09_2020\\\\straight_browning1_photo_05_08_2020_to", all_data$OriginalFile), ]
less_data <- less_data[!grepl("K:\\\\Nelson Lakes\\\\2022-2023\\\\Nest4~St_Ronans\\\\Cavity4a~\\\\D 11_10_2022_to_31_10_2022\\\\Period ending 31_10_22_browning_right_photo", less_data$OriginalFile), ]
less_data <- less_data[!grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2b~_STA39_Raglans\\\\INTERNAL\\\\internal_browning_photo 03_12_2020_to_19_02_2020\\\\nest", less_data$OriginalFile), ]
less_data <- less_data[!grepl("K:\\\\Nelson Lakes\\\\2020-2021\\\\Nest2~Raglan\\\\Cavity2a~_STA26_Raglans\\\\INTERNAL\\\\10_10_2020_to_16_10_2020\\\\internal_borwning1 Photo 10_10_2020_to", less_data$OriginalFile), ]
all_data2 <- rbind(data_subset, less_data)
all_data <- all_data2

# Get monitoring days by burrow for standardisation
all_monitoring_data <- read.csv("C:/Users/petam/Desktop/Critical files/Monitoring_effort_ALTER.csv")
all_monitoring <- pivot_wider(all_monitoring_data, names_from = "Burrow.year", values_from = "Days")
# external
external_monitoring <- all_monitoring[grepl("external", all_monitoring$Camera), ]
totals <- data.frame(Month = "Total", t(colSums(external_monitoring[, -1])))
colnames(totals) <- colnames(external_monitoring)
external_monitoring <- rbind(external_monitoring, totals)
#internal
internal_monitoring <- all_monitoring[grepl("internal", all_monitoring$Camera), ]
totals <- data.frame(Month = "Total", t(colSums(internal_monitoring[, -1])))
colnames(totals) <- colnames(internal_monitoring)
internal_monitoring <- rbind(internal_monitoring, totals)


# make master table
all_table <- all_data
all_table$Camera <- ifelse(grepl("INTERNAL", all_table$OriginalFile), "INTERNAL", "EXTERNAL")
all_table$Hour <- substr(all_table$FirstPhotoNZST, 12, 13)
all_table$Burrow <- vapply(strsplit(all_table$OriginalFile, '\\\\'), function(x)
  paste(x[seq.int(4)], collapse='\\\\'), character(1L))
all_table <- all_table[,c(6,17,18,19)]
all_table <- as.data.frame(table(all_table))
all_table <- pivot_wider(all_table, names_from = "Burrow", values_from = "Freq")

#### INTERNAL
############# Get day totals and make into a dataframe to allow dataframes to be divided
burrow_internal <- all_table[grepl("INTERNAL", all_table$Camera), ]
burrow_internal[, sapply(burrow_internal, function(col) all(col == 0))] <- NA

day_totals_internal <- internal_monitoring[13,]
# Reorder day_totals to match order in burrow_internal
day_totals_internal <- day_totals_internal[, c("K:\\Abel Tasman\\2022-2023\\Nest1~Awapoto nest",
                                               "K:\\Kahurangi\\2017-2018\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2018-2019\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2019-2020\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2020-2021\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2021-2022\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2021-2022\\Nest2~Flora nest",
                                               "K:\\Kahurangi\\2022-2023\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2022-2023\\Nest2~Flora nest",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest3~Skifield",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest3~Skifield",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest4~St_Ronans",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest4~St_Ronans")]
day_totals_internal <- as.numeric(day_totals_internal)

###
# new_row <- setNames(c("extra", day_totals_internal), colnames(burrow_internal))
# for_table_int <- rbind(burrow_internal, new_row)
for_table_int <- burrow_internal
###


day_totals_replicated <- data.frame(matrix(rep(day_totals_internal, each = 24), nrow = 24, byrow = FALSE))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated <- day_totals_replicated2
colnames(day_totals_replicated) <- colnames(burrow_internal)[4:22]
############ divide
storage_animal <- burrow_internal$Animal
storage_hour <- burrow_internal$Hour
storage_camera <- burrow_internal$Camera
burrow_internal <- burrow_internal[,-c(1:3)]
burrow_internal[] <- lapply(burrow_internal, as.numeric)
burrow_internal <- burrow_internal/day_totals_replicated
burrow_internal$Animal <- storage_animal
burrow_internal$Camera <- storage_camera
burrow_internal$Hour <- storage_hour
burrow_internal$Mean <- rowMeans(burrow_internal[, 1:19], na.rm = TRUE)
burrow_internal$SD  <- apply(burrow_internal[, 1:19], 1, sd, na.rm = TRUE)
# ##################################################################
## EXTERNAL
burrow_external <- all_table[grepl("EXTERNAL", all_table$Camera), ]
burrow_external[, sapply(burrow_external, function(col) all(col == 0))] <- NA
day_totals_external <- external_monitoring[13,]
# Reorder day_totals to match order in burrow_external
day_totals_external <- day_totals_external[, c("K:\\Abel Tasman\\2022-2023\\Nest1~Awapoto nest",
                                               "K:\\Kahurangi\\2017-2018\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2018-2019\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2019-2020\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2020-2021\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2021-2022\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2021-2022\\Nest2~Flora nest",
                                               "K:\\Kahurangi\\2022-2023\\Nest1~Cobb nest",
                                               "K:\\Kahurangi\\2022-2023\\Nest2~Flora nest",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2020-2021\\Nest3~Skifield",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest3~Skifield",
                                               "K:\\Nelson Lakes\\2021-2022\\Nest4~St_Ronans",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest1~MOR",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest2~Raglan",
                                               "K:\\Nelson Lakes\\2022-2023\\Nest4~St_Ronans")]

day_totals_external <- as.numeric(day_totals_external)
###
# new_row <- setNames(c("extra", day_totals_external), colnames(burrow_external))
# for_table_ext <- rbind(burrow_external, new_row)
for_table_ext <- burrow_external
###
##godd to
day_totals_replicated <- data.frame(matrix(rep(day_totals_external, each = 24), nrow = 24, byrow = FALSE))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated2 <- as.data.frame(rbind(day_totals_replicated2, day_totals_replicated))
day_totals_replicated <- day_totals_replicated2
colnames(day_totals_replicated) <- colnames(burrow_external)[4:22]
##############THIS IS THE PROBLEM RAGLAN column is filled with NA



############ divide
storage_animal <- burrow_external$Animal
storage_hour <- burrow_external$Hour
storage_camera <- burrow_external$Camera
burrow_external <- burrow_external[,-c(1:3)]
burrow_external[] <- lapply(burrow_external, as.numeric)
burrow_external <- burrow_external/day_totals_replicated
burrow_external$Animal <- storage_animal
burrow_external$Camera <- storage_camera
burrow_external$Hour <- storage_hour
burrow_external$Mean <- rowMeans(burrow_external[, 1:19], na.rm = TRUE)
burrow_external$SD  <- apply(burrow_external[, 1:19], 1, sd, na.rm = TRUE)


# ############### prepare for graphs
daily_activity <- cbind(burrow_internal[,c(20,22,23,24)], burrow_external[,c(23,24)])
colnames(daily_activity) <- c("Animal","Hour","InternalMean","InternalSD","ExternalMean","ExternalSD")
daily_activity$Hour <- as.numeric(as.character(daily_activity$Hour))

#########################################################
daily_activity_plot <- daily_activity[grepl("kea", daily_activity$Animal), ]
# # Create a ggplot line plot without error bands
# ggplot(daily_activity_plot, aes(x = Hour)) +
#   geom_line(aes(y = ExternalMean), color = "blue") +
#   geom_line(aes(y = InternalMean), color = "red") +
#   scale_x_continuous(labels = c(0:23), breaks = c(0:23))+
#   labs(title = "Mean kea activity at an average burrow in a single day (blue = external, red = internal)",
#        x = "Hour",
#        y = "Number of Sessions")
# Create a ggplot line plot with error bands
ggplot(daily_activity_plot, aes(x = Hour)) +
  geom_ribbon(aes(ymin = max(0, ExternalMean - ExternalSD), ymax = ExternalMean + ExternalSD), fill = "blue", alpha = 0.2) +
  geom_ribbon(aes(ymin = max(0, InternalMean - InternalSD), ymax = InternalMean + InternalSD), fill = "red", alpha = 0.2) +
  geom_line(aes(y = ExternalMean), color = "blue") +
  geom_line(aes(y = InternalMean), color = "red") +
  scale_linetype_manual(values = c("solid", "dashed", "dashed")) +
  scale_x_continuous(labels = c(0:23), breaks = c(0:23))+
  labs(title = "Mean kea activity at an average burrow in a single day (blue = external, red = internal)",
       x = "Hour",
       y = "Number of Sessions")

###################3
# internal_table <- for_table_int %>%
#   group_by(Animal) %>%
#   summarize(across(where(is.numeric), sum))
# 
# external_table <- for_table_ext %>%
#   group_by(Animal) %>%
#   summarize(across(where(is.numeric), sum))








##################################################
####################################################
######################################################
# OLD OUTDATED CODE
########################################################
#####################################################
# 
# #####THIS  CODE IS THE PROBLEM. IT IS USED BY the preivous code but has a different order for burrow cols
# #############################################################################
# # Get the total amount of monitoring in each month
# #################################################
# all_monitoring_data <- read.csv("C:/Users/petam/Desktop/Critical files/Monitoring_effort_ALTER.csv")
# ####
# all_monitoring <- pivot_wider(all_monitoring_data, names_from = "Burrow.year", values_from = "Days")
# 
# external_monitoring <- all_monitoring[grepl("external", all_monitoring$Camera), ]
# totals <- data.frame(Month = "Total", t(colSums(external_monitoring[, -1])))
# colnames(totals) <- colnames(external_monitoring)
# external_monitoring <- rbind(external_monitoring, totals)
# external_monitoringv2 <- external_monitoring
# external_monitoringv2$TotalExternal <- rowSums(external_monitoringv2[, 3:21], na.rm = TRUE)
# 
# ####
# internal_monitoring <- all_monitoring[grepl("internal", all_monitoring$Camera), ]
# totals <- data.frame(Month = "Total", t(colSums(internal_monitoring[, -1])))
# colnames(totals) <- colnames(internal_monitoring)
# internal_monitoring <- rbind(internal_monitoring, totals)
# internal_monitoringv2 <- internal_monitoring
# internal_monitoringv2$TotalInternal <- rowSums(internal_monitoringv2[, 3:21], na.rm = TRUE)
# ####
# Month_totals <- as.data.frame(cbind(external_monitoringv2$TotalExternal,internal_monitoringv2$TotalInternal))
# Month_totals <- Month_totals[-13,]
# Month_totals$Month <- c(1:12)
# colnames(Month_totals) <- c("External", "Internal", "Month")
# Month_totals <- pivot_longer(Month_totals, cols = c("External","Internal"), names_to = "Monitoring", values_to = "TotalDays")
# ggplot(Month_totals, aes(x = Month, y = TotalDays, color = Monitoring)) +
#   geom_line(size = 1) +
#   scale_x_continuous(breaks = c(1:12),labels = c("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep", "Oct","Nov","Dec"))+
#   # scale_y_continuous(breaks = 50*(1:12), labels = 50*(1:12),limits = c(0, 600))+
#   scale_color_manual(values=c("#CC6666", "#9999CC"))+
#   ylab("Total days")+
#   ggtitle("Total number of monitoring days in each month across all data (19 burrow seasons)")
# 
