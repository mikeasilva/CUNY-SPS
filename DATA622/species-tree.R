# create the birds dataset
birds<-data.frame(nlegs=rep(2,5),can_fly=c(0,1,1,0,1),height=c(25,40,20,150,10),
color=c('black','black','blue','black','brown')
)
birds2<-cbind(birds,c('chicken','vulture','parrot','ostrich','sparrow'))
chickencolors<-c('black','white','red','mixed')
vulturecolors<-c('grey','black','white')
parrotcolors<-c('teal','green','blue','mixed','pink')
ostrichcolors<-c('grey','black')
sparrowcolors<-c('dark cement','brown')
names(birds2)<-c('nlegs','can_fly','height','color','species')
birds2
#chicken heights mu=25 sd=6
hchicken<-sample(rnorm(10,25,6),5)
#vulture heights mu=40 sd=4
hvulture<-sample(rnorm(10,40,4),5)
hparrot<-sample(rnorm(10,20,2),5)
hostrich<-sample(rnorm(10,150,20),5)
hsparrow<-sample(rnorm(10,10,1),5)
#bigger dataset

#chicken heights mu=25 sd=6
hchicken<-sample(rnorm(10,25,6),5)
#vulture heights mu=40 sd=4
hvulture<-sample(rnorm(10,40,4),5)
hparrot<-sample(rnorm(10,20,2),5)
hostrich<-sample(rnorm(10,150,20),5)
hsparrow<-sample(rnorm(10,10,1),5)

cdset<-rbind(birds2,data.frame(nlegs=rep(2,5),can_fly=rep(0,5), height=hchicken,
color=sample(chickencolors,5,replace=T),species=rep('chicken',5)
))
cdset

#bigger dataset
cdset<-rbind(birds2,data.frame(nlegs=rep(2,5),can_fly=rep(0,5), height=hchicken,
color=sample(chickencolors,5,replace=T),species=rep('chicken',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hvulture,
color=sample(vulturecolors,5,replace=T),species=rep('vulture',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hparrot,
color=sample(parrotcolors,5,replace=T),species=rep('parrot',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(0,5), height=hostrich,
color=sample(ostrichcolors,5,replace=T),species=rep('ostrich',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hsparrow,
color=sample(sparrowcolors,5,replace=T),species=rep('sparrow',5))
)
cdset<-rbind(birds2,data.frame(nlegs=rep(2,5),can_fly=rep(0,5), height=hchicken,
color=sample(chickencolors,5,replace=T),species=rep('chicken',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hvulture,
color=sample(vulturecolors,5,replace=T),species=rep('vulture',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hparrot,
color=sample(parrotcolors,5,replace=T),species=rep('parrot',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(0,5), height=hostrich,
color=sample(ostrichcolors,5,replace=T),species=rep('ostrich',5)),
data.frame(nlegs=rep(2,5),can_fly=rep(1,5), height=hsparrow,
color=sample(sparrowcolors,5,replace=T),species=rep('sparrow',5))
)

# now let us run a tree 

require(rpart)
require(rpart.plot)
set.seed(43)
tridx<-sample(1:30,20,replace=F)
trdata<-cdset[tridx,]
tstdata<-cdset[-tridx,]
trmodel.rpart<-rpart(species~.,data=trdata,minsplit=2)
rpart.plot(trmodel.rpart)
#compare this to
table(trdata$species)/nrow(trdata)

predicted.trmodel.rpart<-predict(trmodel.rpart,trdata[,-5],type='class')
table(trdata[,5],predicted.trmodel.rpart)

# removing colors that are present in test but not in train -- in small dataset
# tree cannot process that
tstdatnw<-tstdata[tstdata$color %in% trdata$color,]
tstdatnw
predicted.tstdatnw.rpart<-predict(trmodel.rpart,tstdatnw[,-5],type='class')
table(tstdatnw[,5],predicted.tstdatnw.rpart)
caret::confusionMatrix( table(tstdatnw[,5],predicted.tstdatnw.rpart))

