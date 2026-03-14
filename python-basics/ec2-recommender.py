import re

sizes = ["nano","micro","small","medium","large","xlarge","2xlarge","4xlarge","8xlarge","16xlarge","32xlarge"]
latest_gen = {"t2":"t3","t3":"t4g","m4":"m5","m5":"m6i","c4":"c5","c5":"c6i","r4":"r5","r5":"r6i"}

RED,GREEN,YELLOW,CYAN,BOLD,RESET = "\033[91m","\033[92m","\033[93m","\033[96m","\033[1m","\033[0m"
STATUS_COLOR = {"Underutilized":YELLOW,"Optimized":GREEN,"Overutilized":RED}

def recommend(instance, cpu):
    t, s = instance.split(".")
    i = sizes.index(s)
    if cpu < 20:
        status, rec, hint = "Underutilized", f"{t}.{sizes[i-1]}" if i > 0 else instance, "⬇ Downsize" if i > 0 else "Already smallest"
    elif cpu <= 80:
        nt = latest_gen.get(t, t)
        status, rec, hint = "Optimized", f"{nt}.{s}", f"⟳ {t}→{nt}" if nt != t else "✔ Latest gen"
    else:
        status, rec, hint = "Overutilized", f"{t}.{sizes[i+1]}" if i < len(sizes)-1 else instance, "⬆ Upsize" if i < len(sizes)-1 else "Already largest"
    return status, rec, hint

def cpu_bar(cpu):
    color = YELLOW if cpu < 20 else GREEN if cpu <= 80 else RED
    return f"{color}[{'█'*round(cpu/5)+'░'*(20-round(cpu/5))}]{RESET} {cpu}%"

def visible(s): return len(re.sub(r'\033\[[0-9;]*m','',str(s)))

def fmt_row(cells, widths, colors=None):
    parts = [f" {(colors[i] if colors else '')+str(c)+RESET}{' '*(widths[i]-visible(c))} " for i,(c,_) in enumerate(zip(cells,widths))]
    return "|" + "|".join(parts) + "|"

def sep(w, c="-"): return "+" + "+".join(c*(x+2) for x in w) + "+"

def print_table(rows):
    headers = ["#","Current EC2","CPU Usage","Status","Recommended","Hint"]
    widths  = [4,14,28,14,14,30]
    print(f"\n{BOLD}{CYAN}  ╔══════════════════════════╗\n  ║  EC2 Rightsizing Advisor ║\n  ╚══════════════════════════╝{RESET}\n")
    print(sep(widths,"═"))
    print(fmt_row(headers, widths, [CYAN]*6))
    print(sep(widths,"═"))
    for i,(cur,cpu,status,rec,hint) in enumerate(rows):
        cells  = [i+1, cur, cpu_bar(cpu), status, rec, hint]
        colors = ["","",""  , STATUS_COLOR.get(status,""), GREEN if rec!=cur else "",""]
        print(fmt_row(cells, widths, colors))
        if i < len(rows)-1: print(sep(widths))
    print(sep(widths,"═"))

rows = []
print(f"\n{BOLD}{CYAN}EC2 Rightsizing Advisor{RESET}\n" + "─"*35)
while True:
    raw = input("\nEC2 instance (or 'done'): ").strip()
    if raw.lower() == "done": break
    parts = raw.split(".")
    if len(parts) != 2 or parts[1] not in sizes: print(f"{RED}✗ Invalid. Use type.size (e.g. t2.large){RESET}"); continue
    cpu_raw = input("CPU utilization (0-100): ").strip()
    if not cpu_raw.isdigit() or not 0 <= int(cpu_raw) <= 100: print(f"{RED}✗ Enter a number 0–100{RESET}"); continue
    status, rec, hint = recommend(raw, int(cpu_raw))
    rows.append((raw, int(cpu_raw), status, rec, hint))
    print(f"  {GREEN}✔ Added{RESET}")

if rows: print_table(rows)
else: print(f"\n{YELLOW}No instances entered.{RESET}\n")