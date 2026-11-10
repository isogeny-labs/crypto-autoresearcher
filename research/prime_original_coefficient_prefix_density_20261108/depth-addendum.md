# Sharper depth and uniform finite bound — frozen review supplement

The original draft's stronger H>K and H<p hypothesis is sufficient but unnecessary. Use instead J=ceil((K+1)/2) and H=2^ceil(log2 J), d=log2 H. Every preimage interval of [0,K] under 2A1+c modp has at most floor(K/2)+1=ceil((K+1)/2)=J integers (K=10M² is even). Thus its residues modulo H are distinct. With p>K and odd p, K+1<=p and J<=ceil(p/2)<=2^(ell−1), where ell=ceil(log2p). Therefore H<=2^(ell−1), d<ell, without the original stronger H<p constraint on nextpow2(K+1). Keep5M<p explicitly; forM>=1,p>10M² already implies it.

The same global prefix bound |G|>=ceil((10M²+1)/3) and conditional bound |C|<=floor(2M²/5)+1 hold. At M1 the ratio bound is1/4. For M>=2, 4*(2M²/5+1)<=(10M²+1)/3 because26M²>=55. Hence |C|/|G|<=1/4 for all integerM>=1, and the guaranteed rejected fraction is at least3/4. Its asymptotic lower bound remains22/25. Retain the exact finite rational bound as the primary statement.

This replaces only the sufficient depth/regime choice for the reviewed final statement; the earlier frozen draft remains valid with its stronger assumptions. All source, clause, projection, global baseline and no-search-frequency limits are unchanged.
