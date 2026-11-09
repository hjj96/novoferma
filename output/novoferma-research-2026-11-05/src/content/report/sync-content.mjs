import {readFileSync, writeFileSync} from "node:fs";
import {fileURLToPath} from "node:url";
import {resolve, dirname} from "node:path";
const folder=dirname(fileURLToPath(import.meta.url));
const root=resolve(folder,"../../..");
const content=JSON.parse(readFileSync(resolve(folder,"content.json"),"utf8"));
const dataPath=resolve(root,"src/data.json");
const data=JSON.parse(readFileSync(dataPath,"utf8"));
const ids=new Set();
for(const section of content.sections||[]){
  if(!section.id || ids.has(section.id)) throw new Error("Each section needs a unique stable id");
  ids.add(section.id);
  const researchQueryId=`research_${section.id.replace(/[^a-zA-Z0-9_-]/g,"_")}`;
  const sectionText=[section.markdown||"",section.after||""].join("\n");
  const sectionLinks=[...sectionText.matchAll(/\[([^\]]+)\]\((https:\/\/[^)]+)\)/g)].map(m=>({label:m[1],url:m[2]}));
  const pdfSections=["overview","baseline","labels","sources"];
  const pdfRows=pdfSections.includes(section.id)?[{label:"Составы пф НОВОФЕРМА.pdf",scope:"Предоставленный пользователем PDF, 13 страниц; массовые доли и закупочные цены отсутствуют"}]:[];
  data.queries[researchQueryId]={rows:[...pdfRows,...sectionLinks],source:{
    label:`Источники раздела: ${section.title}`,
    links:sectionLinks,
    ...(pdfRows.length?{files:["Составы пф НОВОФЕРМА.pdf"]}:{}),
    caveats:["Ссылки поддерживают приведённые факты. Рекомендации, допущения и расчётные сценарии отдельно обозначены в тексте."],
    evidenceFlow:[{title:"Происхождение",detail:"Источники, относящиеся к этому разделу проверенного исследования; не результаты внутреннего производственного учета."}]
  }};
  if(!section.table) continue;
  const queryId=section.table.queryId||`table_${section.id.replace(/[^a-zA-Z0-9_-]/g,"_")}`;
  const previous=data.queries[queryId];
  const markdown=[section.markdown||"",section.after||"",...section.table.rows.flatMap(Object.values)].join("\n");
  const urls=[...markdown.matchAll(/\[([^\]]+)\]\((https:\/\/[^)]+)\)/g)].map(m=>({label:m[1],url:m[2]}));
  data.queries[queryId]={rows:section.table.rows,source:{
    label:section.table.sourceLabel||(section.id==="economics"?"Условные сценарии, не фактическая себестоимость":section.title)||"Таблица исследования",
    classification:section.table.classification||(section.id==="economics"?"scenario":(["guidance","channels","pilots"].includes(section.id)?"analytical-recommendation":"reviewed-research")),
    links:urls,
    caveats:section.table.caveats||["Факты, допущения и предложения различены в тексте раздела. Это исследовательская оценка, не подтверждённая калькуляция производства."],
    metricDefinitions:[{label:section.title||"Таблица",definition:section.table.definition||"Строки из проверенного текста исследования. Область и ограничения приведены рядом с таблицей.",componentIds:[section.id]}],
    evidenceFlow:[{title:"Подготовка таблицы",detail:"Данные перенесены из проверенного содержания отчёта без дополнительных расчетов. Источники указаны в тексте раздела."}],
    ...(previous?.source?.files?{files:previous.source.files}:{})
  }};
}
if(content.sources?.length) data.queries.research_basis.rows=content.sources;
writeFileSync(dataPath,JSON.stringify(data,null,2)+"\n");
console.log(JSON.stringify({sections:ids.size,tables:Object.keys(data.queries).filter(x=>x.startsWith("table_")).length,dataPath}));
