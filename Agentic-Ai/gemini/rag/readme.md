context about your private data



limit context window

So this problem statement is solved by Rag ( Retrival Augment Generation)


- Neive Rag 
pdf to text -> prepare system prompt 

you are ai assistant which can help user talk to their data


Available Data

{ Text}

- Can you tell me about xyz


Sure , This is what i got
now , here is query 2

sure this is 

1M token window

< 50,000 thousand

10 pages

1) indexing phase -> provide the data

- lot of data and chunk it samller
- paragraph

- splitting data

- every chunk

- we use vectore embedding model

- every chunk create vector embedding and we store using vector db


- store vectors
- metadata where i got , date,
- indexing phase

provide some data




2) reteval phase -> chatting with data


- Query - Vectir embedding - user query
- Vector similarity search 
- got only relavent chunks
50 k





- pincone db
- vv8
- wivieat
- qdrant
- 


```base
docker compose up -d detach mode
docker compose up 
 

```




# Lang chain

lot of utility
connecting vector db
ai calls


- loaders
pdf
