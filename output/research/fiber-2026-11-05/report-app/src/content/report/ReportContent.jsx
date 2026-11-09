import React from 'react';
import {RichNarrative, ReportSection, EvidenceChart, DataTable, useDataApp} from '../../data-app-public.jsx';
import blocks from './blocks.json';
import './report.css';
const previews={
 'https://ific.org/wp-content/uploads/2026-IFIC-Food-Health-Survey-Nutrition.pdf':{title:'IFIC 2026: Food & Nutrition',summary:'Взвешенная онлайн-панель США,n=3005,поле22 марта–8 апреля2026. Намерение включать клетчатку62%;это самоотчёт,не измерение потребления.',source:'IFIC',date:'2026-10-07',approvedForReport:true},
 'https://www.spins.com/resources/blog/what-spins-saw-at-expo-west-2026/':{title:'SPINS: Expo West 2026',summary:'Продажи выбранных подкатегорий с маркировочным атрибутом клетчатки. Natural Channel+MULO/Circana,52 недели по22.02.2026. Рост денежный,не в штуках.',source:'SPINS',approvedForReport:true}
};
export function ReportContent(){
 const {appTitle,reviewedRows,visible,canEdit,mode,setAppTitle}=useDataApp();
 return <article className="report-content fiber-report" aria-label="Исследование рынка клетчатки">
 <header className="report-hero"><h1 data-data-app-title contentEditable={canEdit&&mode==='edit'} suppressContentEditableWarning onBlur={canEdit&&mode==='edit'?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}>{appTitle}</h1><RichNarrative id="intro" value="Мировой рынок, Россия и продуктовые решения для «Новофермы». Подготовлено 5 ноября 2026 года." /></header>
 <nav className="fiber-toc" aria-label="Разделы исследования"><a href="#executive">Выводы</a><a href="#pepsi">PepsiCo</a><a href="#russia">Россия</a><a href="#baseline">Наши продукты</a><a href="#law">Маркировка</a><a href="#pilot">План действий</a><a href="#sources">Источники</a></nav>
 {blocks.map(b=>{
 if(!visible(b.id))return null;
 const rows=b.queryId?reviewedRows(b.queryId):[];
 if(b.kind==='chart')return <EvidenceChart key={b.id} id={b.id} queryId={b.queryId} title={b.title} rows={rows} sourceRows={rows} spec={{type:b.id==='fiber-intent'?'bar':'horizontalBar',x:b.x,y:b.y,showValues:true,showLegend:false,startAtZero:true,stackable:false}} height={b.height}/>;
 if(b.kind==='table')return <section key={b.id} id={b.id}><ReportSection id={b.id} queryId={b.queryId} sourceRows={rows} title={b.title}><DataTable rows={rows} columns={b.columns} searchable={false} caption={b.title}/></ReportSection></section>;
 const prose=<RichNarrative id={b.id+':body'} value={b.body} sourcePreviews={previews}/>;
 return <section key={b.id} id={b.id} className={b.id==='executive'?'fiber-summary':undefined}>{b.queryId?<ReportSection id={b.id} queryId={b.queryId} sourceRows={rows} title={b.body.split('\n')[0].replace(/^#+ /,'')} showHeading={false}>{prose}</ReportSection>:prose}</section>
 })}
 </article>
}
