import csv,glob,datetime,statistics,collections,os
from pathlib import Path
base=Path('/mnt/data'); files=sorted(base.glob('ad_viz_plotval_data_20??(1).csv'))
rows=[]; headers=None
for file in files:
 with file.open(newline='',encoding='utf-8-sig') as f:
  r=csv.DictReader(f)
  if headers is None:headers=r.fieldnames
  assert r.fieldnames==headers
  for row in r:
   row['Date']=datetime.datetime.strptime(row['Date'],'%m/%d/%Y').strftime('%Y-%m-%d')
   row['Site ID']=row['Site ID'].zfill(9)
   for k in ('State FIPS Code','County FIPS Code'):
    row[k]=row[k].zfill(2 if k=='State FIPS Code' else 3)
   rows.append(row)
assert len(rows)==52719
values=sorted(float(r['Daily Mean PM2.5 Concentration']) for r in rows)
# Tukey hinges using median of each half
n=len(values);q1=statistics.median(values[:n//2]);q3=statistics.median(values[(n+1)//2:]);iqr=q3-q1;lower=q1-1.5*iqr;upper=q3+1.5*iqr
for r in rows:
 r['Year']=r['Date'][:4]
 r['IQR Outlier Flag']='YES' if not(lower<=float(r['Daily Mean PM2.5 Concentration'])<=upper) else 'NO'
rows.sort(key=lambda r:(r['Date'],r['Site ID'],r['AQS Parameter Code'],int(r['POC'])))
output=base/'COOK_COUNTY_PM25_CLEANED_20261109.csv'
with output.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=headers+['Year','IQR Outlier Flag']);w.writeheader();w.writerows(rows)
flag=sum(r['IQR Outlier Flag']=='YES' for r in rows)
print('q1,q3,iqr,limits,flag',q1,q3,iqr,lower,upper,flag)
print('files',len(files),'rows',len(rows),'output',output,'size',output.stat().st_size)
print('sites by year',dict(sorted(collections.Counter((r['Year'],r['Site ID']) for r in rows).items())[:2]))
