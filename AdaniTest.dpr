program AdaniTest;

uses
  System.StartUpCopy,
  FMX.Forms,
  main in 'main.pas' {MForm};

{$R *.res}

begin
  Application.Initialize;
  Application.CreateForm(TMForm, MForm);
  Application.RegisterFormFamily('Windows', [TMForm]);
  Application.Run;
end.
