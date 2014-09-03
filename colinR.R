# Colin's Solution in R
library(data.table)
library(stringi)
invT<-data.table()
columns<-colnames(raw)
#get the columns that are named Person.X
id_columns<-which(!is.na(stri_match_first(columns,regex='Person.ID')))
id_columns[16]<-252
# stack the investigators
for(id in seq(15))
{
subdata<-raw[,id_columns[id]:(id_columns[id+1]-1)]
if(id<10)
colnames(subdata)<-stri_sub(colnames(subdata),1,-3)
else
colnames(subdata)<-stri_sub(colnames(subdata),1,-4)
not_na<-!all(is.na(subdata))
grants<-raw[not_na,'Grant.Application.ID']
subdata<-cbind(Grant.Application.ID=grants,subdata[not_na,])
invT<-rbind(invT,subdata)
}
# reorder by Application ID
invT<-invT[order(invT$Grant.Application.ID),]
invT[Role=='',Role:='Unk']
# remove subjects who have no id and role
invT<-invT[!(is.na(Person.ID)&Role=='Unk'),]
invT$Role<-factor(invT$Role)
# set new investigator-ids for investigators with roles but no IDs
external<-invT[Role=='EXT_CHIEF_INVESTIGATOR'&is.na(Person.ID),]
ids<-1400000:(1400000+dim(external)[1]-1)
invT[Role=='EXT_CHIEF_INVESTIGATOR'&is.na(Person.ID),Person.ID:=ids]
external<-invT[Role=='STUD_CHIEF_INVESTIGATOR'&is.na(Person.ID),]
ids<-1500000:(1500000+dim(external)[1]-1)
invT[Role=='STUD_CHIEF_INVESTIGATOR'&is.na(Person.ID),Person.ID:=ids]
external<-invT[Role=='STUDRES'&is.na(Person.ID),]
ids<-1600000:(1600000+dim(external)[1]-1)
invT[Role=='STUDRES'&is.na(Person.ID),Person.ID:=ids]
external<-invT[Role=='EXTERNAL_ADVISOR'&is.na(Person.ID),]
ids<-1700000:(1700000+dim(external)[1]-1)
invT[Role=='EXTERNAL_ADVISOR'&is.na(Person.ID),Person.ID:=ids]