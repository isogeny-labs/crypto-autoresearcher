"""Paid point-label equalities and base matches; symbolic targets stay unknown."""

class Registry:
    def __init__(self,fixture,targets,meter,event,base_index=None):
        self.fixture=fixture;self.targets=targets;self.meter=meter;self.event=event;self.nt=len(targets);self.n=len(fixture['factor_base']);self.r=fixture['r'];self.budget=1
        self.labels=[];self.buckets={};self.equations=[];self.dedup=set();self.label_keys=set()
        self.base_index={} if base_index is None else base_index
        if base_index is None:
            for j,atom in enumerate(fixture['factor_base']):self.base_index.setdefault(tuple(atom['point']),[]).append(j);meter.other['affine_base_index_entries']+=1
        else:meter.other['affine_base_index_references']+=1
        self.buckets[None]=[dict(point=None,alpha=0,beta=[0]*self.nt,origin='identity',budget=1)]
    def emit_equation(self,coefficients,outside,rhs,kind,witness):
        r=self.r;coefficients=[v%r for v in coefficients];outside=[v%r for v in outside];rhs%=r
        if not any(coefficients+outside):
            if rhs:raise ValueError('inconsistent public affine coincidence')
            return
        key=tuple(coefficients+outside+[rhs]);self.meter.other['affine_equation_dedup_lookups']+=1
        if key in self.dedup:return
        self.dedup.add(key);row=dict(coefficients=coefficients,outside=outside,rhs=rhs,kind=kind,witness=witness,budget=self.budget)
        self.equations.append(row);self.event(dict(kind='affine_equation',row=row));self.meter.other['affine_equations_retained']+=1
    def add(self,point,alpha,beta,origin):
        f=self.meter.ring;alpha%=self.r;beta=[v%self.r for v in beta]
        if len(beta)!=self.nt:raise ValueError('affine label width')
        key=(point,alpha,tuple(beta));self.meter.other['affine_label_dedup_lookups']+=1
        if key in self.label_keys:return
        self.label_keys.add(key)
        label=dict(point=None if point is None else list(point),alpha=alpha,beta=beta,origin=origin,budget=self.budget)
        self.labels.append(label);self.event(dict(kind='affine_point',record=label));self.meter.other['affine_labels_stored']+=1
        variants=[(point,alpha,beta,1)]
        if point is not None:
            opposite=self.meter.neg(point);variants.append((opposite,f.sub(0,alpha),[f.sub(0,v) if v else 0 for v in beta],-1))
        for image,a,beta0,sign in variants:
            self.label_keys.add((image,a,tuple(beta0)))
            current=dict(point=None if image is None else list(image),alpha=a,beta=beta0,origin=origin,budget=self.budget,sign=sign)
            for old in self.buckets.get(image,[]):
                self.meter.other['affine_collision_bucket_visits']+=1
                outside=[f.sub(x,y) if x!=y else 0 for x,y in zip(beta0,old['beta'],strict=True)];rhs=f.sub(old['alpha'],a)
                self.emit_equation([0]*self.n,outside,rhs,'point_coincidence',dict(left=current,right=old))
            self.buckets.setdefault(image,[]).append(current);self.meter.other['affine_point_bucket_insertions']+=1
        for image,a,beta0,sign in variants:
            self.meter.other['affine_base_lookups']+=1
            for j in self.base_index.get(image,[]):
                self.meter.other['affine_base_matches']+=1
                coefficients=[0]*self.n;coefficients[j]=1
                self.emit_equation(coefficients,[f.sub(0,v) if v else 0 for v in beta0],a,'base_match',dict(atom=j,label=label,sign=sign))
