import concurrent.futures as cof
from time import sleep, time
from sys import stdout


# Asynchrounous Paralel stuff
def concurrent_exec(func_batch, workers, wait=True):
    """
    continously keeps `workers` connections buisy, re-filling from func_batch as pages are completed.
    """
    results = []
    unfillable = 0
    with cof.ThreadPoolExecutor(max_workers = workers) as executor:
        for func in func_batch:
            if isinstance(func,int):
                unfillable = func
                break
            results.append(executor.submit(func))
    if wait:
        cof.wait(results)
    return [r.result() for r in results],unfillable

def batch_concurrent(functions,workers=5,batch_size=20,pause=1,wait=True):
    """
    Repeatedly executes concurrent_exec, until it has exhausted its own que of tasks.
    In between executions,
    """
    data = list()
    
    # Generator that creates generators
    def batch_gen(it,size):
        def this_batch(i,s):
            while s > 0:
                s -= 1
                #print(f"s={s}")
                try:
                    yield next(i)
                except StopIteration:
                    yield s
                    
        while True:
            tst = yield this_batch(it, size)
    
    for batch in batch_gen(functions,batch_size):
        new, unfillable = concurrent_exec(batch,workers, wait)
        data+=new
        if unfillable:
            #print(f"Unfillable was {unfillable}. Exiting.")
            return data
        else:
            #print(f"Waiting for {pause} seconds")
            sleep(pause) 

# Not 100% sure this works propperly. I should do some tests at some point.
def exec_func_stack (initial_values, func_stack, args_ls=None, kwargs_ls=None):
    """
    A generator that produces lambdas that, when called, will call the first function
    on func_stack with initial_value as its first arg, and any additional_args provided.
    
    The second function in func_stack will be run with the result of the first as its first arg, 
    plus any additional_args. This will repeat, until func_stack is exhausted.
    
    A lambda is produced for every initial_value provided.
    
    func_stack: list of functions
    
    initial_value: list/iterable of values
    
    args_gen: list of lists of additoinal arguments.
    
    kwargs_gen: *UNTESTED*  list of dicts of additonal keyworkd arguments.

    """
    #### Checking input ####
    if kwargs_ls is None:
        kwargs_ls = (dict(),)*len(func_stack)
    if args_ls is None:
        args_ls = (tuple(),)*len(func_stack)
    
    elif len(kwargs_ls) < len(func_stack) or len(kwargs_ls) < len(func_stack):
        raise ValueError( "The number of arguments or keywords does"
                          "not match the number of functions present!")

    
    
    def shimfunc(iv, stack, args_ls, kwargs_ls):
            rolling = iv
            for function,args,kwargs in zip(stack, args_ls, kwargs_ls):
                rolling = function(rolling,*args, **kwargs)
            return rolling
        
    for ival in initial_values:
        #print(ival)
        final = lambda i=ival, f=func_stack, a=args_ls, k=kwargs_ls: \
                shimfunc(i, f, a, k)
        yield final

# A debug function to track down a bug wigh regards to extranious values
# ending up in shimfunc's call
def debug_passthrough (val, *args):
    kwargs = dict()
    print(f"Value is {val} ")
    print(f"received {len(args)} arguments. They were:")
    for arg in args:
        print("  ->",arg)
    
    print(f"received {len(kwargs)}. They were:")
    for key,val in kwargs.items():
         print(f" -> {key}:{val}")
    return val
        
# Utility functions for use with exec_func_stack
def message_passthrough (val, message="NoMessage!",f_dict=dict()):
    f_dict['val'] = val
    print(message.format(**f_dict))
    return val


# For use with Queues. Funnily enough, does not require the module to be 
# imported. But that's fine. 
def queued_passthrough(val,message="NoMessage!",queue=None,f_dict=dict()):
    if queue is None:
        raise ValueError("A queue must be provided!")
    f_dict['val'] = val
    queue.put(message.format(**f_dict))
    return val

def queue_halt(queue):
    queue.put(None)

def queue_print(queue, timeout, interval=1):
    eternal = timeout < 0
    end_time = time() + timeout
    while time() < end_time or eternal:
        sleep(interval)
        while not queue.empty() :
            value = queue.get_nowait()
            if value is not None:
                stdout.write(1,bytes(value+"\n"))
            else:
                print("Received 'None', print loop stopping!")
                return
    print("print loop timed out!")

def nb_queue_print (queue, timeout, interval=1 ):
    executor = cof.ThreadPoolExecutor(max_workers = 1)
    executor.submit(queue_print, timeout, interval)
    executor.shutdown()
    
    

