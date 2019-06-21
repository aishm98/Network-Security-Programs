#include"stdio.h"  
#include"stdlib.h"  
#include"sys/types.h"  
#include"sys/socket.h"  
#include"string.h"  
#include"netinet/in.h"  
#include"netdb.h"
  
#define PORT 5000 
#define BUF_SIZE 1024
 
  
int main(int argc, char**argv) {  
    int clientSocket, valRead;
    struct sockaddr_in address, serverAddress;
    char buffer[1024] = {'\0'};

    // Creating socket file descriptor
    clientSocket = socket(AF_INET, SOCK_STREAM, 0) ;
        

    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(PORT);

    // Get server details
    inet_pton(AF_INET, "127.0.0.1", &serverAddress.sin_addr) ;

    
    // Connect to server
    connect(clientSocket, (struct sockaddr *)&serverAddress, sizeof(serverAddress)) ;
    printf("Connected to server\n") ;
 	
    char str1[10], str2[10], str3[10] ; 
	int i ;
 	memset(buffer, 0, BUF_SIZE );
 	//1st part
 		printf("Please enter the message to the server: ");
 		scanf("%s",str1);
		char *msg = str1 ;
		
		// Send Message to server	
		send(clientSocket, msg, strlen(msg), 0) ;
		
		// CLearing the buffer		
		for(i=0;i<1024;i++) buffer[i] = '\0' ;
		
		// Reading data from server into the buffer
		read(clientSocket, buffer, sizeof(buffer));
		printf("Server replied: %s \n", buffer) ;
	
	//2nd Part	
		printf("Please enter the message to the server: ");
 		scanf("%s",str2);
		char *msg2 = str2 ;

		// Send message to server
		send(clientSocket, msg2, strlen(msg2), 0) ;
		
		// Clearing the buffer
		for(i=0;i<1024;i++) buffer[i] = '\0' ;
		
		// Reading data from server into the buffer	
		read(clientSocket, buffer, sizeof(buffer));
		printf("Server replied: %s \n", buffer) ;
		
	//3rd Part
	 	printf("Please enter the message to the server: ");
 		scanf("%s",str3);
		char *msg3 = str3 ;

		// Send message to server
		send(clientSocket, msg3, strlen(msg3), 0) ;

		// Clearing the buffer
		for(i=0;i<1024;i++) buffer[i] = '\0' ;

		// Reading data from server into the buffer
		read(clientSocket, buffer, sizeof(buffer));
		printf("Server replied: %s \n", buffer) ;
		exit(0) ;
		
  	return 0;    
}  
