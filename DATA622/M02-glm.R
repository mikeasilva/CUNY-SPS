unixpath<-"/home/data/ML.Data/heart.csv"
unixecolipath<-"/home/data/ML.Data/ecoli.csv"
path<-"c://Users/rkannan/rk/data/heart.csv"
ecolipath<-"c://Users/rkannan/rk/data/ecoli.csv"
heart<-read.csv(path,header=TRUE,sep=',',stringsAsFactors=FALSE)
ecoli<-read.csv(ecolipath,head=T,sep=',',stringsAsFactors=F)
loadData<-function(csvfile) { read.csv(csvfile,head=T,sep=',',stringsAsFactors=F) }
ecoli_1<-ecoli
ecoli_2<-loadData(ecolipath)
TBL=table(ecoli_1==ecoli_2)
TBL
head(heart)
tail(heart)
dim(heart)
nrow(heart)
ncol(heart)
names(heart)

names(heart)[[1]]<-'age'

(corheart<-cor(heart[,1:13]))

isConstant<-function(x) length(names(table(x)))<2
apply(heart,2,isConstant)

isConstant<-function(x) length(names(table(x)))<2
apply(heart,2,isConstant)

classLabels<-table(heart$target)
print(classLabels)
names(classLabels)
length(names(classLabels))
ifelse(length(names(classLabels))==2,"binary classification", "multi-class classification")

glm_model<-glm(target~.,data=heart, family='binomial')
glm_model
summary_glm_model<-summary(glm_model)
coef_summary_glm_model<-coef(summary_glm_model)
dim(coef_summary_glm_model)
coef_summary_glm_model[[1]]
row.names(coef_summary_glm_model)

coef_summary_glm_model
coef_summary_glm_model[,4]<0.05
row_names<-row.names(coef_summary_glm_model[coef_summary_glm_model[,4]<0.05,])
row_names
summary_glm_model$aic
summary_glm_model$null.deviance
summary_glm_model$deviance
ifelse(summary_glm_model$deviance<summary_glm_model$null.deviance,"model has improved","model has not helped")

if(!require(car))install.packages('car')
library(car)
vif_model<-vif(glm_model)

vif_model
vif_model[vif_model>4]
names(vif_model)
nl<-names(vif_model[vif_model<4])
(newformulastr<-paste('target~',paste(nl,collapse='+')))

Y<-heart[[14]]
head(Y)

actual_distribution<-table(Y)

newmodel<-glm(formulastr,data=heart,family='binomial')
summary(newmodel)
summnewmodel<-summary(newmodel)
(summnewmodel$aic)
(summnewmodel$deviance)
(summnewmodel$null.deviance)
(p_values<-coef(summnewmodel)[,4])

table(p_values<0.005)
predYprob<-predict(newmodel,heart[,1:13],type='response')
predY<-ifelse(predYprob<0.5,0,1)
table(predY)
table(heart[[14]])
table(heart[[14]],predY)
library(caret)
require(caret)

cfm<-caret::confusionMatrix(table(heart[[14]],predY))
cfm

set.seed(43)
tstidx<-sample(1:nrow(heart),0.30*nrow(heart),replace=F)
trdata<-heart[-tstidx,]
tsdata<-heart[tstidx,]

glm.trmodel<-glm(formulastr,data=trdata,family='binomial')
summary(glm.trmodel)
predtr<-predict(glm.trmodel,trdata[,1:13],type='response')

predtrclass<-ifelse(predtr<0.5,0,1)
table(trdata[[14]])
table(predtr)
table(predtrclass)
levels(predtrclass)
levels(trdata[[14]])
length(predtrclass)==length(trdata[[14]])
(trcfm<-caret::confusionMatrix(table(trdata[[14]],predtrclass)))

predts<-predict(glm.trmodel,tsdata[,1:13],type='response')
predtsclass<-ifelse(predts<0.5,0,1)
table(predtsclass)
table(tsdata[[14]])
table(tsdata[[14]],predtsclass)
tscfm<-caret::confusionMatrix(table(tsdata[[14]],predtsclass))
tscfm
#https://stackoverflow.com/questions/13548092
(precision <- tscfm$byClass['Pos Pred Value'])    
(recall <- tscfm$byClass['Sensitivity'])
(f_measure <- 2 * ((precision * recall) / (precision + recall))) #geometric mean instead of arithmatic mean

tst.model2<-glm(target~cp+ca+thal+oldpeak,data=trdata,family='binomial')
summary(tst.model2)
tr.tst.pred<-predict(tst.model2,trdata[,1:13],family='binomial')
tr.pred.class<-ifelse(tr.tst.pred<0.5,0,1)
tr.pred.table<-table(trdata[[14]],tr.pred.class)
tr.pred.table
(tr.pred.cfm<-confusionMatrix(tr.pred.table))
(precision <- tr.pred.cfm$byClass['Pos Pred Value'])    #https://stackoverflow.com/questions/13548092
(recall <- tr.pred.cfm$byClass['Sensitivity'])
(f_measure <- 2 * ((precision * recall) / (precision + recall)))


tst.pred2<-predict(tst.model2,tsdata[,1:13],type='response')
tst.pred2.class<-ifelse(tst.pred2<0.5,0,1)
tst.pred2.table<-table(tsdata[[14]],tst.pred2.class)
tst.pred2.table
(tst.pred2.cfm<-confusionMatrix(tst.pred2.table))
(accuracy<-tst.pred2.cfm$overall['Accuracy'])
(precision <- tst.pred2.cfm$byClass['Pos Pred Value'])    #https://stackoverflow.com/questions/13548092
(recall <- tst.pred2.cfm$byClass['Sensitivity'])
(f_measure <- 2 * ((precision * recall) / (precision + recall)))

graphics.off() 
par("mar") 
par(mar=c(1,1,1,1))
if(!require(pROC))install.packages('pROC')
library(pROC)
par(pty="s") 
glmROC <- roc(tsdata[[14]]~ tst.pred2.class,plot=TRUE,
print.auc=TRUE,col="green",lwd =4,
legacy.axes=TRUE,main="ROC Curves")

# Let us plot using ROCR packages

getMetrics<-function(actual_class,predicted_response)
{
X=list()
if ( require(ROCR) ) {
auc_1=prediction(predicted_response,actual_class)
prf=performance(auc_1, measure="tpr",x.measure="fpr")
slot_fp=slot(auc_1,"fp")
slot_tp=slot(auc_1,"tp")

fpr=unlist(slot_fp)/unlist(slot(auc_1,"n.neg"))
tpr=unlist(slot_tp)/unlist(slot(auc_1,"n.pos"))

auc<-performance(auc_1,"auc")
AUC<-auc@y.values[[1]]
X=list(fpr=fpr,tpr=tpr,auc=AUC)
}
X
}

L<-getMetrics(tsdata[[14]],tst.pred2)
plot(L$fpr,L$tpr,main=" ROC Plot tpr vs fpr")
print(paste("AUC=",L$auc,sep=''))


