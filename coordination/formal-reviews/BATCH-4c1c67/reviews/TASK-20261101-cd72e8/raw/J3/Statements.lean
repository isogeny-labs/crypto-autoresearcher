import CryptoResearch.Nagao.Lemma4Witness
import CryptoResearch.Nagao.Lemma4Outside
import CryptoResearch.Nagao.RecoveryRule
import CryptoResearch.Nagao.Bridge
import CryptoResearch.Nagao.BridgeB

set_option pp.proofs false

open CryptoResearch.Nagao

/-! ## Named theorems: elaborated types -/
#check @Lemma4Witness.lemma4_inside_false
#check @Lemma4Outside.lemma4_outside_false
#check @RecoveryRule.recovery
#check @Bridge.lemma4_mv_false
#check @Bridge.red_sum_red
#check @BridgeB.lemma4_mvB_false
/- supporting witness-level theorems -/
#check @Lemma4Witness.lemma4_inside_false_A
#check @Lemma4Witness.lemma4_inside_false_B
#check @Lemma4Witness.A_dF
#check @Lemma4Witness.A_dF'
#check @Lemma4Witness.B_dF
#check @Lemma4Witness.B_dF'
#check @Lemma4Outside.lemma4_outside_false_B
#check @Lemma4Outside.lemma4_outside_fe_false_B
#check @Bridge.firstFall_out
#check @Bridge.firstFall_in
#check @Bridge.out_no_fall_two
#check @Bridge.in_no_fall_two
#check @Bridge.no_fall_one
#check @Bridge.fake_fall_two
#check @Bridge.fake_fall_two_fe
#check @BridgeB.firstFall_outB
#check @BridgeB.firstFall_inB
#check @BridgeB.out_no_fall_twoB
#check @BridgeB.in_no_fall_twoB
#check @BridgeB.no_fall_one3
#check @BridgeB.fake_fall_twoB
#check @BridgeB.fake_fall_two_feB

/-! ## Definitions (RecoveryRule / Bridge / BridgeB) -/
#print RecoveryRule.IsFall
#print RecoveryRule.IsFakeFall
#print RecoveryRule.withFe
#print RecoveryRule.red
#print RecoveryRule.clamp
#print RecoveryRule.fe
#print RecoveryRule.deg
#print Bridge.FirstFallIs
#print Bridge.Lemma4Mv
#print BridgeB.FirstFallIs'
#print BridgeB.Lemma4Mv'
#print Bridge.toMv
#print Bridge.expOf
#print Bridge.mA₁
#print Bridge.mA₂
#print Bridge.mFA
#print Bridge.Gout
#print Bridge.Gin
#print Bridge.gFake
#print BridgeB.mB₁
#print BridgeB.mB₂
#print BridgeB.mFB
#print BridgeB.GoutB
#print BridgeB.GinB
#print BridgeB.gFakeB

/-! ## Definitions (list model) -/
#print Lemma4Witness.FirstFall
#print Lemma4Witness.FallAt
#print Lemma4Witness.Cond
#print Lemma4Witness.Adm
#print Lemma4Witness.gens
#print Lemma4Witness.prep
#print Lemma4Witness.reduceFe
#print Lemma4Witness.mul
#print Lemma4Witness.monoMul
#print Lemma4Witness.norm
#print Lemma4Witness.mons
#print Lemma4Witness.monsAux
#print Lemma4Witness.DegLe
#print Lemma4Witness.fieldEqs
#print Lemma4Witness.Lemma4Inside
#print Lemma4Outside.Lemma4Outside
#print Lemma4Outside.Lemma4OutsideFe
#print Lemma4Witness.SA
#print Lemma4Witness.SB
#print Lemma4Witness.fA₁
#print Lemma4Witness.fA₂
#print Lemma4Witness.fB₁
#print Lemma4Witness.fB₂
#print Lemma4Outside.FA
#print Lemma4Outside.FB
#print Lemma4Witness.gA_true
#print Lemma4Witness.gA_fake
#print Lemma4Witness.gB_true
#print Lemma4Witness.gB_fake
#print Lemma4Outside.gA_out
#print Lemma4Outside.gB_out
