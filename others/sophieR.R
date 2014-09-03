# Sophie's solution

grants_table <- data.frame(raw[,1:26])
investigators_table <- data.frame(raw[,27:252])
#there is one column X, which only has NAs and will be left out
nr_cols_per_inv <- floor(length(investigators_table)/15)
tidy_train <- data.frame(raw[,1:(26+15)])
for (i in c(2:15)) {
new_stack <- raw[,c((1:26), (((((i-1)*15)+1):(i*15))) +26)]
colnames(new_stack) <- colnames(tidy_train)
tidy_train <- rbind(tidy_train, new_stack)
}
names(tidy_train)[27:length(tidy_train)] <- c("Person.ID", "Role", "Year.of.Birth", "Country.of.Birth", "Home.Language", 
"Dept.No.", "Faculty.No.", "With.PHD", "No..of.Years.in.Uni.at.Time.of.Grant", 
"Number.of.Successful.Grant", "Number.of.Unsuccessful.Grant", "A.", "A", "B", "C")
# check if investigator is there, decision: if there is no ID and no role(except for the 98 cases where there is no 1st investigator at all) 
ind_to_omit <- which(is.na(tidy_train$Person.ID) & (tidy_train$Role == ''))
tidy_train <- tidy_train[-ind_to_omit,]