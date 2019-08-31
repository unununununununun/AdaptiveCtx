unit main;

interface

uses
  System.SysUtils, System.Types, System.UITypes, System.Classes, System.Variants,
  FMX.Types, FMX.Controls, FMX.Forms, FMX.Graphics, FMX.Dialogs, FMX.Objects, FMX.Layouts,Windows,Messages, FMX.StdCtrls, FMX.Effects;

type
  TMForm = class(TForm)
    topl: TLayout;
    toplr: TRectangle;
    mlayout: TLayout;
    SizeGrip1: TSizeGrip;
    Rectangle1: TRectangle;
    GlowEffect1: TGlowEffect;
    procedure toplrMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Single);
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  MForm: TMForm;

implementation

{$R *.fmx}

procedure TMForm.toplrMouseDown(Sender: TObject; Button: TMouseButton; Shift: TShiftState; X, Y: Single);
 var
  hw : HWND;
begin
 hw := FindWindow(nil,PChar(MForm.Caption));
 ReleaseCapture;
 SendMessage(hw, WM_SysCommand,61458,0);
end;

end.
