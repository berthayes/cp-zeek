#!/bin/sh


key="/home/ubuntu/.ssh/id_rsa"


if [ $1 = "c" ]; then
	for i in `cat c3_nodes.txt`; 
	do /usr/bin/scp -i $key $2 $i:/home/ubuntu/$2 && echo && echo "File $2 copied to $(/usr/bin/nslookup $i | grep name | awk {'print $4'}), I suppose";
	done

elif [ $1 = "a" ]; then
	for i in `cat all_nodes.txt`;
	do /usr/bin/scp -i $key $2 $i:/home/ubuntu/$2 && echo && echo "File $2 copied to $(/usr/bin/nslookup $i | grep name | awk {'print $4'}), I suppose";
	done

elif [ $1 = "k" ]; then
	for i in `cat ksqldb_nodes.txt`;
	do /usr/bin/scp -i $key $2 $i:/home/ubuntu/$2 && echo && echo "File $2 copied to $(/usr/bin/nslookup $i | grep name | awk {'print $4'}), I suppose";
        done
	
fi
