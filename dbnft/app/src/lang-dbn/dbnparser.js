// This file was generated by lezer-generator. You probably shouldn't edit it.
import {LRParser} from "@lezer/lr"
export const parser = LRParser.deserialize({
  version: 13,
  states: ")rQYQPOOOwQPO'#C`OOQO'#Cd'#CdO!_QQO'#CcO!fQSO'#CqO!nQWO'#CuO|QQO'#CxO!sQPO'#CzO|QQO'#C}OOQO'#C_'#C_OOQO'#DP'#DPQYQPOOO!xQPO,58zO#PQPO'#CjO|QQO'#CkO|QQO'#ClOOQO'#Cg'#CgOOQO'#DQ'#DQO#XQQO,58}OOQO,58},58}O|QQO'#CsO#`QPO,59]O|QQO,59]O|QQO,59aO|QQO,59dO#eQ`O,59fOOQO,59i,59iOOQO-E6}-E6}OOQO1G.f1G.fO#pQPO1G.fO#wQQO,59UO|QQO,59VO$OQPO,59WOOQO'#Cm'#CmOOQO-E7O-E7OOOQO1G.i1G.iO|QQO,59_OOQO1G.w1G.wO$ZQPO1G.wO|QQO1G.{O$`QPO1G/OOOQO'#DR'#DRO$eQ`O1G/QOOQO1G/Q1G/QO$`QPO1G/QOOQO7+$Q7+$QOOQO1G.p1G.pO$pQQO1G.pO$wQPO1G.qO|QQO,59YO|QQO,59YOOQO1G.r1G.rO$|QPO1G.yOOQO7+$c7+$cO$`QPO7+$gOOQO7+$j7+$jOOQO-E7P-E7POOQO7+$l7+$lO$`QPO7+$lOOQO7+$[7+$[OOQO7+$]7+$]O%RQPO1G.tOOQO1G.t1G.tO|QQO7+$eOOQO<<HR<<HROOQO<<HW<<HWOOQO<<HP<<HP",
  stateData: "%g~OxOSPOS~OTPOXQOYQOfSOjTOmUOoVOrWOyXO~Oy[O~O[`O]`Oz]O|^O!O_O~OycO~P|OhfO|dO~OkgO~OYiO~OUlO~PYOXQOYQO~OysO~P|OyuO~OTPOpyOy|O~OU}O~PYO{!OO~P|Oc!ROd!SO!P!TO~Oy!VO~OTPO~OTPOpyOy![O~O{!]O~P|O}!^O~O}!aO~Od!SOcbi!Pbi~OofjmrXmY~",
  goto: "%TvPPPw}PP!e!kPP!tPP#r#r#r$W$aPP!eP$fP!ePP!eP!ePP!eP$i$s$}XYOZ[mWXOZ[mQ{iQ!XxS!Zz|Q!b!WR!c![XXOZ[mWROZ[mRn]WaRbn!PQhUQjWQo^Uq_!R!SQtdQvfQwgQxhQ!QoQ!UtQ!WwR!d!au`RUW^_bdfghnotw!P!R!S!aQp_Q!_!RR!`!SVq_!R!SReSQZOSkZmRm[QbRSrb!PR!PnQziR!Yz",
  nodeNames: "⚠ LineComment Program Statement Block { } Command CommandName BuiltinCommand CommandIdentifier Expression Number VariableGet NumberCall DotGet ParenthesizedExpression ExpressionGivenWereParenthesized BinaryOperation AddOperators MulOperators SetStatement Set DotSet VariableSet RepeatStatement Repeat RepeatArg QuestionStatement Question DefineCommand ProcedureDef FormalArg ValueStatement Value",
  maxTerm: 47,
  skippedNodes: [0,1],
  repeatNodeCount: 3,
  tokenData: "Fr~R!RXY$[YZ$apq$[xy$fyz$kz{$p{|$u}!O$u!P!Q$z!Q!R%_!R!S%_!S!T%_!T!U%_!U!V%_!V!W%_!W!X%_!X!Y%_!Y!Z%_!Z![%_!^!_&S!`!a&X!c!e&^!e!f&w!f!n&^!n!o+i!o!p&^!p!q.]!q!r&^!r!s9a!s!t&^!t!u<u!u!v@v!v!x&^!x!yCS!y!}&^!}#OF^#P#QFc#T#V&^#V#W&w#W#b&^#b#c.]#c#f&^#f#g<u#g#h@v#h#j&^#j#kCS#k#o&^#o#pFh#q#rFm~$aOx~~$fOy~~$kO!O~~$pO!P~~$uOd~~$zOc~~%PPd~!P!Q%S~%XQP~OY%SZ~%S~%dY[~!Q!R%_!R!S%_!S!T%_!T!U%_!U!V%_!V!W%_!W!X%_!X!Y%_!Y!Z%_!Z![%_~&XOz~~&^O{~o&kSp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#o&^o'UUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#c&^#c#d'h#d#o&^o'uUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#a&^#a#b(X#b#o&^o(fUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#a&^#a#b(x#b#o&^o)VTp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U)f#U#o&^o)sUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#b&^#b#c*V#c#o&^o*dUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#W&^#W#X*v#X#o&^o+TTp`kW]QhSYPpq+d!Q![&^!c!}&^#R#S&^#T#o&^P+iOoPo+vUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#]&^#]#^,Y#^#o&^o,gUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#b&^#b#c,y#c#o&^o-WUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y-j#Y#o&^o-wTp`kW]QhSYPpq.W!Q![&^!c!}&^#R#S&^#T#o&^P.]OXPo.jWp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#c&^#c#d/S#d#i&^#i#j6o#j#o&^o/aUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#h&^#h#i/s#i#o&^o0QUp`kW]QhSYP!Q![&^!c!u&^!u!v0d!v!}&^#R#S&^#T#o&^o0qVp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U1W#U#a&^#a#b3a#b#o&^o1eUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#a&^#a#b1w#b#o&^o2UUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y2h#Y#o&^o2uTp`kW]QhSYP!Q![&^!a!b3U!c!}&^#R#S&^#T#o&^P3XPpq3[P3aOmPo3nTp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U3}#U#o&^o4[Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#`&^#`#a4n#a#o&^o4{Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#`&^#`#a5_#a#o&^o5lUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y6O#Y#o&^o6]Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#f&^#f#g2h#g#o&^o6|Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#a&^#a#b7`#b#o&^o7mUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U&^#U#V8P#V#o&^o8^Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y8p#Y#o&^o8}Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#f&^#f#g*v#g#o&^o9nVp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U:T#U#X&^#X#Y<U#Y#o&^o:bUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#d&^#d#e:t#e#o&^o;RUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y;e#Y#o&^o;rUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#f&^#f#g-j#g#o&^o<cUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#b&^#b#c-j#c#o&^o=SUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y=f#Y#o&^o=sUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#d&^#d#e>V#e#o&^o>dUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#Y>v#Y#o&^o?TTp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U?d#U#o&^o?qUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#h&^#h#i@T#i#o&^o@bTp`kW]QhSYPpq@q!Q![&^!c!}&^#R#S&^#T#o&^P@vOjPoATXp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#U1W#U#X&^#X#YAp#Y#a&^#a#b3a#b#o&^oA}Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#h&^#h#iBa#i#o&^oBnTp`kW]QhSYPpqB}!Q![&^!c!}&^#R#S&^#T#o&^PCSOfPoCaTp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#UCp#U#o&^oC}Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#`&^#`#aDa#a#o&^oDnUp`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#i&^#i#jEQ#j#o&^oE_Up`kW]QhSYP!Q![&^!c!}&^#R#S&^#T#X&^#X#YEq#Y#o&^oFQSp`kW]QhSrPYP!Q![&^!c!}&^#R#S&^#T#o&^~FcO|~~FhO}~~FmOT~~FrOU~",
  tokenizers: [0, 1, 2, 3, 4],
  topRules: {"Program":[0,2]},
  tokenPrec: 198
})

