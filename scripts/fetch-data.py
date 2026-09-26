#!/usr/bin/env python3
import json,os,urllib.parse,urllib.request
BASE="https://pumperly.com/api/stations"
COUNTRIES={"DK":(8.0,54.4,15.5,57.9),"SE":(10.5,55.0,24.5,69.2),"NO":(4.0,57.8,31.5,71.5)}
FUELS={"sp95":["E10","E5"],"sp98":["E5_98","E98_E10","E5_PREMIUM"],"diesel":["B7","B7_PREMIUM"],"el":["EV"]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"TankPris/1.0"})
 with urllib.request.urlopen(req,timeout=45) as r:return json.load(r)
def tiles(b,c=3,r=3):
 a,b1,d,e=b; out=[]
 for x in range(c):
  for y in range(r):
   out.append((a+(d-a)*x/c,b1+(e-b1)*y/r,a+(d-a)*(x+1)/c,b1+(e-b1)*(y+1)/r))
 return out
def norm(f,cc,fuel):
 p=f.get("properties") or {}; g=f.get("geometry") or {}; co=g.get("coordinates") or [None,None]
 try: price=float(p.get("price"))
 except: price=None
 return {"id":str(p.get("id") or p.get("externalId") or ""), "name":p.get("name") or "Tankstation", "brand":p.get("brand") or "", "address":p.get("address") or "", "city":p.get("city") or "", "lat":co[1], "lng":co[0], "price":price, "currency":p.get("currency") or ("DKK" if cc=="DK" else "SEK" if cc=="SE" else "NOK"), "reportedAt":p.get("reportedAt"), "country":cc, "fuelType":p.get("fuelType") or fuel}
os.makedirs("data",exist_ok=True)
for cc,b in COUNTRIES.items():
 for fuel,codes in FUELS.items():
  d={}
  for code in codes:
   for minlon,minlat,maxlon,maxlat in tiles(b):
    try:o=fetch(BASE+"?"+urllib.parse.urlencode({"bbox":f"{minlon},{minlat},{maxlon},{maxlat}","fuel":code}))
    except Exception as e: print("WARN",cc,fuel,code,e); continue
    for feat in o.get("features",[]):
     row=norm(feat,cc,fuel)
     if row["id"]: d[row["id"]]=row
  rows=sorted(d.values(),key=lambda x:(x["city"],x["name"],x["id"]))
  out={"country":cc,"fuel":fuel,"updatedAtSource":max([x["reportedAt"] for x in rows if x.get("reportedAt")] or [None]),"stations":rows}
  path=f"data/{cc}-{fuel}.json"; new=json.dumps(out,ensure_ascii=False,separators=(",",":"))+"\n"
  if not os.path.exists(path) or open(path,encoding="utf-8").read()!=new: open(path,"w",encoding="utf-8").write(new)
  print(cc,fuel,len(rows))