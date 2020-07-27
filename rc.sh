#!/bin/sh


key="/Users/bhayes/Downloads/bert_confluent_aws_keypem.pem"


if [ $1 = "c" ]; then
	for i in `cat connect_nodes.txt`; 
	do /usr/bin/ssh -i $key $i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess";
	done



elif [ $1 = "a" ]; then
	for i in `cat all_nodes.txt`;
	do /usr/bin/ssh -i $key $i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess";
	done

elif [ $1 = "k" ]; then
	for i in `cat ksqldb_nodes.txt`;
	do /usr/bin/ssh -i $key ubuntu@$i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess"
	done

fi


