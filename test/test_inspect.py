import inspect,colorama

def DEBUG(text,status="INFO"):
    colors={"INFO":colorama.Fore.LIGHTBLUE_EX,"ERROR":colorama.Fore.LIGHTRED_EX,"DEBUG":colorama.Fore.LIGHTMAGENTA_EX,"WARNING":colorama.Fore.LIGHTYELLOW_EX}
    previous_frame = inspect.currentframe().f_back
    (filename, lineno, 
     function_name, lines, index) = inspect.getframeinfo(previous_frame)
    print( f'{colorama.Fore.CYAN}{filename}:{lineno}{colorama.Fore.RESET}->{colors[status]}{status}{colorama.Style.RESET_ALL}:{colors[status]}{text}{colorama.Style.RESET_ALL}')
