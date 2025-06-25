#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
    struct Node* prev;
} Node;

int main() {
    Node* node1 = (Node*) malloc(sizeof(Node));
    Node* node2 = (Node*) malloc(sizeof(Node));
    Node* node3 = (Node*) malloc(sizeof(Node));
    Node* node4 = (Node*) malloc(sizeof(Node));

    node1->data = 3;
    node2->data = 5;
    node3->data = 13;
    node4->data = 2;

    node1->next = node2;
    node1->prev = node4;  // Circular link

    node2->prev = node1;
    node2->next = node3;

    node3->prev = node2;
    node3->next = node4;

    node4->prev = node3;
    node4->next = node1;  // Circular link

    printf("\nTraversing forward:\n");
    Node* currentNode = node1;
    Node* startNode = node1;
    printf("%d -> ", currentNode->data);
    currentNode = currentNode->next;

    while (currentNode != startNode) {
        printf("%d -> ", currentNode->data);
        currentNode = currentNode->next;
    }
    printf("...\n");  // Indicating the list loops back

    printf("\nTraversing backward:\n");
    currentNode = node4;
    startNode = node4;
    printf("%d -> ", currentNode->data);
    currentNode = currentNode->prev;

    while (currentNode != startNode) {
        printf("%d -> ", currentNode->data);
        currentNode = currentNode->prev;
    }
    printf("...\n");  // Indicating the list loops back

    free(node1);
    free(node2);
    free(node3);
    free(node4);

    return 0;
}