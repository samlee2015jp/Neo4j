sentence = 'I go to aist in Tokyo everyday. I go to school every weekday. Everyone plays game at home, where I donot play.'

//createentity1
create (n1:entity1{name:'I'})-[r1:next]->(n2:entity1{name:'go'})-[r2:next]->(n3:entity1{name:'to'})-[r3:next]->(n4:entity1{name:'AIST'})-[r4:next]->(n5:entity1{name:'in'})-[r5:next]->(n6:entity1{name:'Tokyo'})-[r6:next]->(n7:entity1{name:'everyday'})-[r7:next]->(n8:entity1{name:'.'})

// createentity2
match (n:entity1{name:'to'}),(m:entity1{name:'.'}),create (n)-[r:next]->(n1:entity2{name:'school'})-[r1:next]->(n2:entity2{name:'every'})-[r2:next]->(n3:entity2{name:'weekday'})-[r3:next]->(m)

//  createentity3
match (n:entity1{name:'.'}),(m:entity1{name:'I'}),create (n)-[r:next]->(n1:entity3{name:'Everyone'})-[r1:next]->(n2:entity3{name:'plays'})-[r2:next]->(n3:entity3{name:'game'})-[r3:next]->(n4:entity3{name:'at'})-[r4:next]->(n5:entity3{name:'home'})-[r5:next]->(n6:entity3{name:','})-[r6:next]->(n7:entity3{name:'where'})-[r7:next]->,(m)-[rm:next]->,(n8:entity3{name:'donot'})-[r8:next]->(n9:entity3{name:'play'})-[r9:next]->(n)

//createRelationHeadTail
match (n{name:'I'}),(m{name:'.'})
create (m)-[r:head]->(n),(m)<-[r1:tail]-(n)

//CreatePrevNextRelation
match (n)-[r:next]->(m)
create (n)<-[p:prev]-(m)