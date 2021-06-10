Search.setIndex({docnames:["hyperaggregate","hyperaggregate.aggregation_profiles","hyperaggregate.aggregation_profiles.impl","hyperaggregate.aggregation_profiles.impl.utils","hyperaggregate.client","hyperaggregate.client.utils","hyperaggregate.netutils","hyperaggregate.server","hyperaggregate.server.utils","hyperaggregate.shared","index","modules"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":3,"sphinx.domains.rst":2,"sphinx.domains.std":2,sphinx:56},filenames:["hyperaggregate.rst","hyperaggregate.aggregation_profiles.rst","hyperaggregate.aggregation_profiles.impl.rst","hyperaggregate.aggregation_profiles.impl.utils.rst","hyperaggregate.client.rst","hyperaggregate.client.utils.rst","hyperaggregate.netutils.rst","hyperaggregate.server.rst","hyperaggregate.server.utils.rst","hyperaggregate.shared.rst","index.rst","modules.rst"],objects:{"":{hyperaggregate:[0,0,0,"-"]},"hyperaggregate.aggregation_profiles":{abstract_aggregation_profile:[1,0,0,"-"],impl:[2,0,0,"-"]},"hyperaggregate.aggregation_profiles.abstract_aggregation_profile":{AbstractAggregationProfile:[1,1,1,""]},"hyperaggregate.aggregation_profiles.abstract_aggregation_profile.AbstractAggregationProfile":{aggregate:[1,2,1,""],create_shares_on_prepared_data:[1,2,1,""],prepare:[1,2,1,""],unprepare:[1,2,1,""]},"hyperaggregate.aggregation_profiles.impl":{additive_sharing_model_profile:[2,0,0,"-"],torch_additive_sharing_model_profile:[2,0,0,"-"],utils:[3,0,0,"-"]},"hyperaggregate.aggregation_profiles.impl.additive_sharing_model_profile":{AverageAdditiveSharingModelProfile:[2,1,1,""]},"hyperaggregate.aggregation_profiles.impl.additive_sharing_model_profile.AverageAdditiveSharingModelProfile":{aggregate:[2,2,1,""],create_shares_on_prepared_data:[2,2,1,""],prepare:[2,2,1,""],unprepare:[2,2,1,""]},"hyperaggregate.aggregation_profiles.impl.torch_additive_sharing_model_profile":{AverageTorchAdditiveSharingModelProfile:[2,1,1,""]},"hyperaggregate.aggregation_profiles.impl.torch_additive_sharing_model_profile.AverageTorchAdditiveSharingModelProfile":{prepare:[2,2,1,""],unprepare:[2,2,1,""]},"hyperaggregate.aggregation_profiles.impl.utils":{dictutils:[3,0,0,"-"],numberutils:[3,0,0,"-"],secret_sharing:[3,0,0,"-"],torchutils:[3,0,0,"-"]},"hyperaggregate.aggregation_profiles.impl.utils.dictutils":{map_dict:[3,3,1,""]},"hyperaggregate.aggregation_profiles.impl.utils.numberutils":{convert_to_float_array:[3,3,1,""],convert_to_int_array:[3,3,1,""]},"hyperaggregate.aggregation_profiles.impl.utils.secret_sharing":{create_additive_shares:[3,3,1,""],create_int_additive_shares:[3,3,1,""],rand_interval:[3,3,1,""],reconstruct_additive_secretsharing_result:[3,3,1,""]},"hyperaggregate.aggregation_profiles.impl.utils.torchutils":{convert_numpy_state_dict_to_torch:[3,3,1,""],convert_state_dict_to_numpy:[3,3,1,""]},"hyperaggregate.client":{privacy_preserving_aggregator:[4,0,0,"-"],utils:[5,0,0,"-"]},"hyperaggregate.client.privacy_preserving_aggregator":{ClientState:[4,1,1,""],PrivacyPreservingAggregator:[4,1,1,""]},"hyperaggregate.client.privacy_preserving_aggregator.ClientState":{DOING_JOB:[4,4,1,""],NO_JOB:[4,4,1,""],WAITING_JOB:[4,4,1,""],WAITING_SIGNUP_CONFIRMATION:[4,4,1,""]},"hyperaggregate.client.privacy_preserving_aggregator.PrivacyPreservingAggregator":{aggregate:[4,2,1,""],register_callbacks:[4,2,1,""],time_elapsed:[4,5,1,""]},"hyperaggregate.client.utils":{aggregation_model_queue:[5,0,0,"-"],partial_model_message:[5,0,0,"-"]},"hyperaggregate.client.utils.aggregation_model_queue":{AggregationModelQueue:[5,1,1,""]},"hyperaggregate.client.utils.aggregation_model_queue.AggregationModelQueue":{add:[5,2,1,""],get:[5,2,1,""],is_empty:[5,2,1,""]},"hyperaggregate.client.utils.partial_model_message":{PartialModelMessage:[5,1,1,""]},"hyperaggregate.netutils":{abstract_message_router:[6,0,0,"-"],message:[6,0,0,"-"],zmqsockets:[6,0,0,"-"]},"hyperaggregate.netutils.abstract_message_router":{AbstractMessageRouter:[6,1,1,""]},"hyperaggregate.netutils.abstract_message_router.AbstractMessageRouter":{address:[6,5,1,""],debug:[6,5,1,""],register_callbacks:[6,2,1,""],send:[6,2,1,""],start:[6,2,1,""],stop:[6,2,1,""]},"hyperaggregate.netutils.message":{Message:[6,1,1,""],MessageType:[6,1,1,""]},"hyperaggregate.netutils.message.MessageType":{AGGREGATION_SIGNUP:[6,4,1,""],FINAL_PARTIAL_SHARES:[6,4,1,""],GROUP_ASSIGNMENT:[6,4,1,""],HEALTH_CHECK:[6,4,1,""],HEALTH_CONFIRMATION:[6,4,1,""],MODEL_UPDATE:[6,4,1,""],NO_MODEL_NEEDED:[6,4,1,""],PARTIAL_MODEL_SHARE:[6,4,1,""],SIGNUP_CONFIRMATION:[6,4,1,""]},"hyperaggregate.netutils.zmqsockets":{MessageWrapper:[6,1,1,""],ZMQDirectSocket:[6,1,1,""]},"hyperaggregate.netutils.zmqsockets.ZMQDirectSocket":{address:[6,5,1,""],send:[6,2,1,""],start:[6,2,1,""],stop:[6,2,1,""]},"hyperaggregate.server":{privacy_preserving_server:[7,0,0,"-"],utils:[8,0,0,"-"]},"hyperaggregate.server.privacy_preserving_server":{SchedulingServer:[7,1,1,""]},"hyperaggregate.server.privacy_preserving_server.SchedulingServer":{register_callbacks:[7,2,1,""]},"hyperaggregate.server.utils":{aggregation_tree_generation:[8,0,0,"-"]},"hyperaggregate.server.utils.aggregation_tree_generation":{generate_aggregation_tree:[8,3,1,""],partition_sizes:[8,3,1,""]},"hyperaggregate.shared":{aggregation_tree:[9,0,0,"-"],responsive_message_router:[9,0,0,"-"]},"hyperaggregate.shared.aggregation_tree":{AggregationGroup:[9,1,1,""],AggregationTree:[9,1,1,""]},"hyperaggregate.shared.responsive_message_router":{ResponsiveMessageRouter:[9,1,1,""]},"hyperaggregate.shared.responsive_message_router.ResponsiveMessageRouter":{register_callbacks:[9,2,1,""]},hyperaggregate:{aggregation_profiles:[1,0,0,"-"],client:[4,0,0,"-"],netutils:[6,0,0,"-"],server:[7,0,0,"-"],shared:[9,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","attribute","Python attribute"],"5":["py","property","Python property"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:attribute","5":"py:property"},terms:{"0":[3,4,6],"1":[3,4,6],"2":[4,6],"3":[4,6,8],"4":6,"5":6,"6":6,"7":6,"8":6,"abstract":[1,6],"class":[1,2,4,5,6,7,9],"default":9,"enum":[4,6],"float":[2,3,4],"function":[3,5,6,9],"import":6,"int":[1,2,3],"return":[1,3,4,5,6,7,9],"true":5,"while":3,A:[3,4,9],If:[4,5],Is:6,It:3,The:[1,3,6,9],abc:[1,6],about:3,abstract_aggregation_profil:[0,2,11],abstract_message_rout:[0,9,11],abstractaggregationprofil:[1,2],abstractmessagerout:[6,9],accept:[3,6],activ:6,actor:9,add:5,addit:[3,6],additive_sharing_model_profil:[0,1],address:[4,5,6,9],afterward:2,aggreg:[1,2,3,4,5,9],aggregation_actor:9,aggregation_id:5,aggregation_model_queu:[0,4],aggregation_profil:[0,7,11],aggregation_signup:6,aggregation_tre:[0,11],aggregation_tree_gener:[0,7],aggregationgroup:9,aggregationmodelqueu:5,aggregationtre:9,agreg:9,aim:6,all:5,alreadi:[1,5],also:1,amount:4,an:[3,6],analogu:3,ani:3,anoth:3,anymor:[5,6],appear:9,appli:3,applic:1,appropri:6,ar:[3,5],around:5,arr:3,arrai:[2,3],arrrai:3,assign:4,associ:[6,7,9],assum:9,assumpt:3,attribut:6,avail:5,averag:2,averageadditivesharingmodelprofil:2,averagetorchadditivesharingmodelprofil:2,axi:3,back:3,base:[1,2,4,5,6,7,9],basi:[1,6],being:[3,4],between:[4,6,9],boilerpl:6,bool:[5,6],bound:3,built:3,call:2,callback:[4,6,7,9],can:[1,4,5],client:[0,2,9,11],clientstat:4,code:[1,6],collect:3,commun:6,concret:[1,2,3],constructor:5,content:11,contribut:2,convert:[2,3],convert_numpy_state_dict_to_torch:3,convert_state_dict_to_numpi:3,convert_to_float_arrai:3,convert_to_int_arrai:3,corespond:[6,7,9],correspond:4,count:2,creat:[1,2,3],create_additive_shar:3,create_int_additive_shar:3,create_shares_on_prepared_data:[1,2],data:[1,2],debug:6,debug_mod:[4,6,7,9],decim:3,decimals_includ:3,defin:2,deprec:3,dest_addr:6,dest_address:6,destin:6,dict:[3,6,7,9],dictionari:[2,3,6,7,9],dictutil:[1,2],digit:3,digits_to_keep:2,divid:2,doing_job:4,each:3,easi:5,effect:6,element:2,empti:5,equival:3,except:5,exhang:6,fals:[4,5,6,7,9],final_partial_shar:6,finish:4,first:2,form:[1,3],from:[3,5,6],gener:9,generate_aggregation_tre:8,get:5,getter:[4,6],given:[2,3,5],group:[5,9],group_assign:6,group_id:5,group_siz:7,ha:[4,5],handl:[1,5],health_check:6,health_confirm:6,helper:[3,5],hide:6,high:3,highest:9,hyperaggreg:11,id:9,identifi:[5,9],impl:[0,1],implement:[1,2,3,5,6,9],includ:[3,6],index:10,indic:6,inform:[3,6],initi:[3,6],initliaz:6,input:3,insid:5,instead:3,int64:3,integr:6,interfac:6,intern:6,interv:3,invers:3,is_empti:5,is_root_level:9,k:3,kei:[3,6,7,9],last:[3,4],level:9,list:[1,3,5,9],logic:[1,2,4,5],low:3,lower:3,map:3,map_dict:3,map_funct:3,mathemat:3,messag:[0,4,5,7,9,11],message_typ:6,messagetyp:[6,7,9],messagewrapp:6,method:[2,3,6,7,9],min_subset_s:8,mode:6,model:[2,4,5,9],model_upd:6,modul:[10,11],mtrand:3,name:6,netutil:[0,9,11],network:[1,6,9],next:5,no_job:4,no_model_need:6,node:6,none:[4,6],np:3,num_actor:[7,8],num_shar:[1,2,3],number:[1,2,3,4],number_to_split:3,numberutil:[1,2],numpi:[2,3],numpy_state_dict:3,object:[1,3,4,5,6,7,9],obtain:3,on_message_received_callback:6,onli:6,oper:3,order:[6,9],ordereddict:3,other:2,otherwis:5,out:3,output:3,over:[1,3],packag:[10,11],page:10,paramet:[1,3,4,5,6],parent:2,part:5,partial:[2,5],partial_model_messag:[0,4],partial_model_shar:6,partialmodelmessag:5,particip:[5,8,9],participating_nod:9,particular:3,partition_s:8,pass:3,payload:6,peer:[6,9],place:4,point:3,port:7,possibl:[4,6],prepar:[1,2],prepared_data:[1,2],prepared_shar:[1,2],preserv:3,presum:5,privacy_preserving_aggreg:[0,11],privacy_preserving_serv:[0,11],privacypreservingaggreg:4,process:6,profil:3,proper:4,properti:[4,6],protect:6,provid:[1,6],pytorch:[2,3],queue:5,rais:5,rand:3,rand_interv:3,random:3,randomst:3,rang:3,readi:1,receiv:[1,5,6],recommend:3,reconstruct_additive_secretsharing_result:3,register_callback:[4,6,7,9],repres:[2,4,6,9],represent:3,respons:9,responsive_message_rout:[0,4,7,11],responsivemessagerout:[4,7,9],rest:1,retriev:5,risen:5,role:9,rout:6,run:6,s:[2,5],same:3,sampl:3,sampler_funct:3,schedulingserv:7,search:10,second:4,secret_shar:[1,2],secur:1,send:[1,6],sender:6,sender_addr:6,sent:[1,5],server:[0,9,11],server_address:4,set:[5,6],set_siz:8,shape:3,share:[0,1,2,3,4,5,7,11],should:[3,6,7,9],side:5,sign:4,signup_confirm:6,simplyf:6,singl:[1,9],size:[3,8],socket:6,some:1,specif:9,specifi:[1,3,5,6],split:[1,2,3],src:10,start:[4,6],state:[2,3,4,6],state_dict:[2,3],stop:6,store:5,str:[3,5,6,7,9],string:3,submodul:[0,11],subpackag:11,subset_s:8,sum:[2,3],taken:4,target_s:7,tensor:3,them:[2,6],thi:[2,3,5,6,9],thread:6,throughout:1,time:4,time_elaps:4,torch:3,torch_additive_sharing_model_profil:[0,1],torchutil:[1,2],transfer:1,transform:[1,2],tree:9,tupl:[2,3],type:[1,3,4,5,6,7,9],under:[3,9],uniqu:9,unit:1,unprepar:[1,2],up:4,upper:3,us:[1,3],usabl:1,util:[0,1,2,4,7],v:3,valu:[3,4,6,7,9],valueerror:5,variabl:[5,9],wait:[4,6],waiting_job:4,waiting_signup_confirm:4,when:6,where:[2,3],whether:[6,9],which:[1,5,6,9],wrap:6,wrapper:[5,6],yet:4,zeromq:6,zmqdirectsocket:6,zmqsocket:[0,11]},titles:["hyperaggregate package","hyperaggregate.aggregation_profiles package","hyperaggregate.aggregation_profiles.impl package","hyperaggregate.aggregation_profiles.impl.utils package","hyperaggregate.client package","hyperaggregate.client.utils package","hyperaggregate.netutils package","hyperaggregate.server package","hyperaggregate.server.utils package","hyperaggregate.shared package","Welcome to HyperAggregate\u2019s documentation!","src"],titleterms:{abstract_aggregation_profil:1,abstract_message_rout:6,additive_sharing_model_profil:2,aggregation_model_queu:5,aggregation_profil:[1,2,3],aggregation_tre:9,aggregation_tree_gener:8,client:[4,5],content:[0,1,2,3,4,5,6,7,8,9,10],dictutil:3,document:10,hyperaggreg:[0,1,2,3,4,5,6,7,8,9,10],impl:[2,3],indic:10,messag:6,modul:[0,1,2,3,4,5,6,7,8,9],netutil:6,numberutil:3,packag:[0,1,2,3,4,5,6,7,8,9],partial_model_messag:5,privacy_preserving_aggreg:4,privacy_preserving_serv:7,responsive_message_rout:9,s:10,secret_shar:3,server:[7,8],share:9,src:11,submodul:[1,2,3,4,5,6,7,8,9],subpackag:[0,1,2,4,7],tabl:10,torch_additive_sharing_model_profil:2,torchutil:3,util:[3,5,8],welcom:10,zmqsocket:6}})