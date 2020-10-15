
file<-'c:/Users/rk215/data/heart.csv' # change this to run in your env
heart<-read.csv(file,head=T,sep=',',stringsAsFactors=F)
head(heart)
catheart<-heart[,c(2,3,6,7,9,11,12,13,14)]
require(rpart)
require(rpart.plot)
head(catheart,20)
catheart$target<-as.factor(catheart$target)
set.seed(43)
tridx<-sample(1:nrow(catheart),0.7*nrow(catheart),replace=F)
trdata<-catheart[tridx,]
tstdata<-catheart[-tridx,]
trmodel.rpart<-rpart(target~.,data=trdata,minsplit=2)
rpart.plot(trmodel.rpart)
table(trdata$target)/nrow(trdata) # compare this to the root node lables

predicted.trmodel.rpart<-predict(trmodel.rpart,trdata[,-9],type='class')
TBL<-table(trdata[,9],predicted.trmodel.rpart)

caret::confusionMatrix(TBL)

predicted.tstmodel.rpart<-predict(trmodel.rpart,tstdata[,-9],type='class')
TSTTBL<-table(tstdata[,9],predicted.tstmodel.rpart)

caret::confusionMatrix(TSTTBL)

#Summary
#Individual trees are prone to over-fitting so performance degrades over never seen 
# before data as we see here 
