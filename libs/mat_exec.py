#!/usr/bin/env python
# coding: utf-8

# In[1]:


import mat_definitions as md
import asyncrequest as ar


# In[2]:


pages = md.list_of_pages()
print(pages)
bpr = ar.batch_page_request(pages,batch_size=20)
res = bpr.run()
print(res)
bpr.save("./Matdump2.csv")