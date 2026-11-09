import React from 'react';
export type SceneSpec={id:string;start:number;frames:number;kind:'side'|'punch'|'mg'|'h3'|'video'|'screen'|'promo';variant?:string;title?:string;eyebrow?:string;lines?:string[];items?:{label:string;text:string}[];foot?:string;asset?:string;trimBefore?:number;through_body?:boolean;screen?:{asset:string;name:string;width:number;height:number;focus:[number,number,number,number]}};
export type Plan={status?:string;technical_demo?:boolean;captions_burned?:boolean;sound_events?:{at:number;kind:string}[];version:number;fps:number;width:number;height:number;frames:number;presenter?:string|null;foreground?:string|null;audio_source?:string|null;background?:string|null;mask?:string|null;mediaPreview?:string|null;scenes:SceneSpec[]};
export const MediaContext=React.createContext<string|null>(null);
export const SceneContext=React.createContext<SceneSpec|null>(null);
