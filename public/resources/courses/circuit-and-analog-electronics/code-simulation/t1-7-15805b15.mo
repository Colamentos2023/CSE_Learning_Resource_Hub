model T1_7
  Modelica.Electrical.Analog.Basic.Resistor resistor(T_ref=273.15,R=5.1e3) 
    annotation (Placement(transformation(origin={-137.814,-22.9607}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Basic.Resistor resistor1(T_ref=273.15,R=12.334e3) 
    annotation (Placement(transformation(origin={-104.126,43.3731}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor2(T_ref=273.15,R=40e3) 
    annotation (Placement(transformation(origin={-137.839,43.1653}, 
extent={{-10,-10},{10,10}}, 
rotation=90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor4(T_ref=273.15,R=1e3) 
    annotation (Placement(transformation(origin={-89.7658,-22.651}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor(C=30e-6) 
    annotation (Placement(transformation(origin={-166.422,-22.6302}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor1(C=30e-6) 
    annotation (Placement(transformation(origin={-49.1268,26.1542}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Capacitor capacitor2(C=30e-6) 
    annotation (Placement(transformation(origin={-61.0802,0.920894}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Basic.Ground ground 
    annotation (Placement(transformation(origin={-64.558,-51.9471}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Semiconductors.NPN npn(Phie=0.7) 
    annotation (Placement(transformation(origin={-111.952,6.60881}, 
extent={{-10,-10},{10,10}})));
  Modelica.Electrical.Analog.Sources.ConstantVoltage constantVoltage(V=15) 
    annotation (Placement(transformation(origin={25.434,15.2203}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Sources.SineVoltage sineVoltage(V(displayUnit="mV")=0.015,f=1000) 
    annotation (Placement(transformation(origin={-26.6081,-19.1488}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  Modelica.Electrical.Analog.Basic.Resistor resistor3(T_ref=273.15,R=5.1e3) 
    annotation (Placement(transformation(origin={2.2557,-5.74203}, 
extent={{-10,-10},{10,10}}, 
rotation=270)));
  annotation(Diagram(coordinateSystem(extent={{-100,-100},{100,100}}, 
grid={2,2})));
equation
  connect(resistor4.n, ground.p) 
  annotation(Line(origin={-90,-41}, 
points={{0.2342,8.349},{0.2342,-0.947113},{25.442,-0.947113}}, 
color={0,0,255}));
  connect(resistor4.n, resistor.n) 
  annotation(Line(origin={-114,-33}, 
points={{24.2342,0.349},{24.2342,-9.06357},{-23.814,-9.06357},{-23.814,0.0393}}, 
color={0,0,255}));
  connect(capacitor.n, resistor.n) 
  annotation(Line(origin={-152,-38}, 
points={{-14.4223,5.36977},{-14.4223,-3.65565},{14.186,-3.65565},{14.186,5.0393}}, 
color={0,0,255}));
  connect(resistor2.p, resistor.p) 
  annotation(Line(origin={-138,10}, 
  points={{0.160592,23.1653},{0.160592,-22.9607},{0.186,-22.9607}}, 
  color={0,0,255}));
  connect(resistor.p, capacitor.p) 
  annotation(Line(origin={-152,-13}, 
points={{14.186,0.0393},{14.186,19.4652},{-14.4223,19.4652},{-14.4223,0.369769}}, 
color={0,0,255}));
  connect(npn.B, resistor.p) 
  annotation(Line(origin={-131,0}, 
points={{9.048,6.60881},{-6.814,6.60881},{-6.814,-12.9607}}, 
color={0,0,255}));
  connect(resistor1.p, npn.C) 
  annotation(Line(origin={-105,23}, 
points={{0.874,10.3731},{8.93613,10.3731},{8.93613,-10.39119},{3.048,-10.39119}}, 
color={0,0,255}));
  connect(npn.E, resistor4.p) 
  annotation(Line(origin={-97,-6}, 
points={{-4.952,6.60881},{7.2342,6.60881},{7.2342,-6.651}}, 
color={0,0,255}));
  connect(capacitor1.p, npn.C) 
  annotation(Line(origin={-95,20}, 
points={{35.8732,6.15418},{3.90087,6.15418},{3.90087,-7.39119},{-6.952,-7.39119}}, 
color={0,0,255}));
  connect(constantVoltage.p, resistor1.n) 
  annotation(Line(origin={-39,39}, 
  points={{64.434,-13.7797},{64.434,14.3731},{-65.126,14.3731}}, 
  color={0,0,255}));
  connect(resistor1.n, resistor2.n) 
  annotation(Line(origin={-121,53}, 
  points={{16.874,0.373104},{-16.8394,0.373104},{-16.8394,0.165262}}, 
  color={0,0,255}));
  connect(constantVoltage.n, ground.p) 
  annotation(Line(origin={-32,-22}, 
points={{57.434,27.2203},{57.434,-19.9471},{-32.558,-19.9471}}, 
color={0,0,255}));
  connect(sineVoltage.p, capacitor2.n) 
  annotation(Line(origin={-46,-4}, 
points={{19.3919,-5.1488},{19.3919,4.920894},{-5.08015,4.920894}}, 
color={0,0,255}));
  connect(sineVoltage.n, ground.p) 
  annotation(Line(origin={-64,-39}, 
points={{37.3919,9.85119},{37.3919,-2.9471},{-0.558,-2.9471}}, 
color={0,0,255}));
  connect(capacitor2.p, resistor4.p) 
  annotation(Line(origin={-72,-6}, 
points={{0.919848,6.920894},{-17.7658,6.920894},{-17.7658,-6.651}}, 
color={0,0,255}));
  connect(capacitor1.n, resistor3.p) 
  annotation(Line(origin={-18,15}, 
  points={{-21.1268,11.1542},{20.2557,11.1542},{20.2557,-10.742}}, 
  color={0,0,255}));
  connect(resistor3.n, ground.p) 
  annotation(Line(origin={-31,-29}, 
  points={{33.2557,13.258},{33.2557,-12.9471},{-33.558,-12.9471}}, 
  color={0,0,255}));
  end T1_7;