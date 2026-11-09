import React from 'react';
export type SceneSpec={id:string;start:number;frames:number;kind:'side'|'punch'|'mg'|'h3'|'screen';variant?:string;eyebrow?:string;lines?:string[];foot?:string;asset?:string;through_body?:boolean;screen?:{asset:string;name:string;width:number;height:number;focus:[number,number,number,number]}};
export type Plan={status?:string;sound_events?:{at:number;kind:string}[];version:number;fps:number;width:number;height:number;frames:number;presenter?:string|null;mask?:string|null;mediaPreview?:string|null;scenes:SceneSpec[]};
export const MediaContext=React.createContext<string|null>(null);
export const SceneContext=React.createContext<SceneSpec|null>(null);
