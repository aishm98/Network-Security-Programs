#include <unistd.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <netinet/in.h>
#include <string.h>

#define PORT 5000												// Port Number defined here

int main() {
    int serverSocket, clientSocket, newsocket;
    
    pid_t childpid ;
    char clientAddr[100];
    
    struct sockaddr_in address, cl_addr;
    int addrLen = sizeof(address);
    int opt = 1;
    char buffer[1024] = {'\0'};
	int i ;
    // Creating socket file descriptor
    if ((serverSocket = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Error while creating socket");
        exit(EXIT_FAILURE);
    }
	printf("Socket created at port : %d \n", PORT);
	
    address.sin_family = AF_INET;
    address.sin_port = htons(PORT);
    address.sin_addr.s_addr = INADDR_ANY;

    // Attaching socket to the port as defined
    if (bind(serverSocket, (struct sockaddr *)&address, sizeof(address))) {
        perror("Error while binding");
        exit(EXIT_FAILURE);
    }

    // Listen on the socket created
    if (listen(serverSocket, 5) < 0) {
        perror("Error while listening");
        exit(EXIT_FAILURE);
    }
    
    // Accept client
    newsocket = accept(serverSocket, (struct sockaddr *)&address, (socklen_t *)&addrLen);
	printf("Connected with client socket number %d \n", newsocket);
	inet_ntop(AF_INET, &(cl_addr.sin_addr), clientAddr, 100);

    char str1[] = "Hello from server" ;
    char str2[] = "Goodbye" ;

	// --- 1st part --- //
	// Clearing the buffer
	for( i=0 ; i<1024 ; i++ ) buffer[i] = '\0' ;								
	
	// Getting data from client into the buffer
	read(newsocket, buffer, sizeof(buffer));									
	printf("Client socket %d sent message: %s \n", newsocket, buffer) ;
	
	// Send message to client
	char *msg = str1 ;
	send(newsocket, msg, strlen(msg), 0);
	printf("Replied to client %d \n", newsocket) ;
	
	// --- 2nd part --- //
	// Clearing the buffer
	for(i=0;i<1024;i++) buffer[i] = '\0' ;
	read(newsocket, buffer, sizeof(buffer));
	printf("Client socket %d sent message: %s \n", newsocket, buffer) ;
	
	// Taking values of the operands and operator	
	int op1 = buffer[0] - '0';
	int op2 = buffer[2] - '0';
	char sign = buffer[1] ;
	int result ;
	// Calculating the result
	if(sign == '+')
		result = op1 + op2 ;
	else if(sign == '-')
		result = op1 - op2 ;
	else if(sign == '*')
		result = op1 * op2 ;
	else if(sign == '/')	
		result = op1 / op2 ;
	
	char ch = '0' + result ;
	char str3[10] ;
	strcpy(str3,buffer) ;
	int len = strlen(str3) ;
	str3[len] = '=' ;
	str3[len+1] = ch ;

	// Sending data to client
	char *msg3 = str3 ;
	send(newsocket, msg3, strlen(msg3), 0);
	printf("Replied to client %d \n", newsocket) ;	
		
	// 3rd part	
	for(i=0;i<1024;i++) buffer[i] = '\0' ;
	read(newsocket, buffer, sizeof(buffer));
	printf("Client socket %d sent message: %s \n", newsocket, buffer) ;
		
	char *msg2 = str2 ;
	send(newsocket, msg2, strlen(msg2), 0);
	printf("Replied to client %d \n", newsocket) ;
	printf("Client said bye; finishing\n") ;
    
    close(newsocket) ;
    
    return 0;
}
